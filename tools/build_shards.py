"""build_shards.py — Day 2: 轻量清洗/去重 → tokenize → 6:4 混配 → uint16 memmap 分片

输入（D-06，与 train_tokenizer.py 同源）：
  zh = data/raw/minimind_dataset/pretrain_t2t.jsonl（中文主力）
  en = data/raw/fineweb-edu/sample/10BT/*.parquet（英文主力，14 分片）
输出：
  data/shards/shard-000.bin …（默认 1GB/片 = 536,870,912 token，uint16，值域 < 32000）
  data/shards/val.bin（默认 ~4M token，文档级哈希留出，与 train 不共享文档）
  data/shards/meta.json · SHA256SUMS（指纹入库）· 可选 data/bpe-smoke/ 换轨冒烟切片
流水线（HANDOFF §7 Day 2 清单 3~5）：
  1. 清洗轻量版：CRLF→LF、strip、长度过滤（100 ≤ chars ≤ 50,000）——不做启发式强清洗
  2. 精确哈希去重：blake2b-64(规范化全文)，两语言共享集合（MinHash 近似去重留 Day 9 缓冲）
  3. val 划分：hash % 500 == 0 的文档进 val（文档级、随机、无泄漏），预算满后多余候选丢弃
  4. 混配比：**token 级** 60% en / 40% zh——按累计缺口动态选语言（文档粒度近似，最终截断到预算）
  5. 每文档尾接 EOS（<|endoftext|>=0）；训练端按 1024 固定窗口切
  6. 值域断言前置数据侧：每次 flush 检查 max id < vocab_size（Day 1 教训）
用法（仓库根目录，建议 tmux）：
  `.venv-pre/bin/python -I tools/build_shards.py 2>&1 | tee logs/day2-build-<stamp>.log`
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from tokenizers import Tokenizer


# ---------------------------------------------------------------- 语料读取

def iter_zh_raw(path: str):
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                doc = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = doc.get("text", "")
            if text:
                yield str(text)


def iter_en_raw(parquet_dir: str):
    import pyarrow.parquet as pq

    for p in sorted(Path(parquet_dir).glob("*.parquet")):
        pf = pq.ParquetFile(p)
        for i in range(pf.metadata.num_row_groups):
            col = pf.read_row_group(i, columns=["text"]).column(0)
            for text in col.to_pylist():
                if text:
                    yield text


# ---------------------------------------------------------------- 清洗/去重/划分

class DocFilter:
    """规范化 + 长度过滤 + 精确去重 + 哈希 val 划分（两语言共享去重集合）。"""

    def __init__(self, val_mod: int, val_targets: dict, min_chars: int, max_chars: int):
        self.val_mod = val_mod
        self.val_targets = val_targets
        self.min_chars = min_chars
        self.max_chars = max_chars
        self.seen: set[int] = set()
        self.val_counts = {"en": 0, "zh": 0}  # 由主循环同步更新（实际写入数）
        self.stats = {
            lang: {"read": 0, "short": 0, "long": 0, "dup": 0,
                   "val_kept": 0, "val_dropped": 0, "train_docs": 0}
            for lang in ("en", "zh")
        }

    def feed(self, text: str, lang: str):
        """返回 (kind, text, nchars, nbytes)；丢弃返回 None。"""
        st = self.stats[lang]
        st["read"] += 1
        text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
        nchars = len(text)
        if nchars < self.min_chars:
            st["short"] += 1
            return None
        if nchars > self.max_chars:
            st["long"] += 1
            return None
        raw = text.encode("utf-8")
        h = int.from_bytes(hashlib.blake2b(raw, digest_size=8).digest(), "little")
        if h in self.seen:
            st["dup"] += 1
            return None
        self.seen.add(h)
        if h % self.val_mod == 0:
            if self.val_counts[lang] >= self.val_targets[lang]:
                st["val_dropped"] += 1
                return None
            st["val_kept"] += 1
            return ("val", text, nchars, len(raw))
        st["train_docs"] += 1
        return ("train", text, nchars, len(raw))


# ---------------------------------------------------------------- 编码流

def encoded_stream(lang: str, raw_iter, flt: DocFilter, tok: Tokenizer,
                   eos_id: int, vocab_size: int, batch_bytes: int = 4_000_000):
    """批式编码（batch_bytes 聚合后一次 encode_batch，兼顾吞吐与文档级混配）。"""
    pending: list[tuple[str, str, int, int]] = []
    pending_bytes = 0

    def encode_pending():
        encs = tok.encode_batch([t for _, t, _, _ in pending], add_special_tokens=False)
        for (kind, text, nchars, nbytes), enc in zip(pending, encs):
            ids = np.empty(len(enc.ids) + 1, dtype=np.uint16)
            ids[:-1] = enc.ids
            ids[-1] = eos_id  # 文档边界
            assert int(ids.max()) < vocab_size, f"编码越界 id {int(ids.max())} ≥ vocab {vocab_size}"
            yield kind, ids, nchars, nbytes

    for text in raw_iter:
        got = flt.feed(text, lang)
        if got is None:
            continue
        pending.append(got)
        pending_bytes += got[3]
        if pending_bytes >= batch_bytes:
            yield from encode_pending()
            pending, pending_bytes = [], 0
    if pending:
        yield from encode_pending()


# ---------------------------------------------------------------- 落盘

class TokenSink:
    """缓冲写 uint16；shard_tokens=None → 单文件，否则按片滚动并逐片记 SHA256。"""

    def __init__(self, out_dir: Path, prefix: str, vocab_size: int, shard_tokens: int | None):
        self.out_dir = out_dir
        self.prefix = prefix
        self.vocab_size = vocab_size
        self.shard_tokens = shard_tokens
        self.buf: list[np.ndarray] = []
        self.buf_tokens = 0
        self.total = 0
        self.cur = 0
        self.f = None
        self.h = None
        self.cur_name = ""
        self.files: list[dict] = []
        self.flush_threshold = 8_000_000

    def add(self, ids: np.ndarray) -> None:
        if len(ids) == 0:
            return
        self.buf.append(ids)
        self.buf_tokens += len(ids)
        if self.buf_tokens >= self.flush_threshold:
            self._flush()

    def _open_next(self) -> None:
        idx = len(self.files)
        self.cur_name = (f"{self.prefix}.bin" if self.shard_tokens is None
                         else f"{self.prefix}-{idx:03d}.bin")
        self.f = (self.out_dir / self.cur_name).open("wb")
        self.h = hashlib.sha256()
        self.cur = 0

    def _close_cur(self) -> None:
        assert self.f is not None and self.h is not None
        self.f.close()
        self.files.append({"name": self.cur_name, "tokens": self.cur, "sha256": self.h.hexdigest()})
        self.f = self.h = None

    def _flush(self) -> None:
        if not self.buf:
            return
        arr = np.concatenate(self.buf)
        self.buf, self.buf_tokens = [], 0
        assert int(arr.max()) < self.vocab_size, f"分片越界 id {int(arr.max())} ≥ vocab {self.vocab_size}"
        pos = 0
        while pos < len(arr):
            if self.f is None:
                self._open_next()
            space = (self.shard_tokens - self.cur) if self.shard_tokens is not None else len(arr) - pos
            take = arr[pos:pos + space]
            raw = np.ascontiguousarray(take, dtype=np.uint16).tobytes()
            self.f.write(raw)
            self.h.update(raw)
            self.cur += len(take)
            self.total += len(take)
            pos += len(take)
            if self.shard_tokens is not None and self.cur >= self.shard_tokens:
                self._close_cur()

    def close(self) -> None:
        self._flush()
        if self.f is not None:
            self._close_cur()


# ---------------------------------------------------------------- 主流程

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizer", default="data/tokenizer-32k/tokenizer.json")
    ap.add_argument("--zh-src", default="data/raw/minimind_dataset/pretrain_t2t.jsonl")
    ap.add_argument("--en-dir", default="data/raw/fineweb-edu/sample/10BT")
    ap.add_argument("--out-dir", default="data/shards")
    ap.add_argument("--target-tokens", type=int, default=3_000_000_000)
    ap.add_argument("--en-ratio", type=float, default=0.6, help="en 占比（D-06 补充拍板 6:4）")
    ap.add_argument("--shard-gb", type=float, default=1.0, help="单片大小 GB（uint16 → 2 字节/token）")
    ap.add_argument("--val-tokens", type=int, default=4_000_000)
    ap.add_argument("--val-mod", type=int, default=500, help="hash %% val_mod == 0 的文档进 val")
    ap.add_argument("--min-chars", type=int, default=100)
    ap.add_argument("--max-chars", type=int, default=50_000)
    ap.add_argument("--smoke-tokens", type=int, default=50_000_000, help="换轨冒烟 train 切片；0=不生成")
    ap.add_argument("--smoke-val-tokens", type=int, default=2_000_000)
    ap.add_argument("--smoke-dir", default="data/bpe-smoke")
    ap.add_argument("--report-csv", default="reports/2026-11-18-day2-shards.csv")
    args = ap.parse_args()

    assert 0.0 < args.en_ratio < 1.0
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tok = Tokenizer.from_file(args.tokenizer)
    vocab_size = tok.get_vocab_size()
    assert vocab_size <= 65535, f"uint16 装不下 vocab {vocab_size}"
    eos_id = tok.token_to_id("<|endoftext|>")
    assert eos_id is not None and eos_id >= 0, "tokenizer 缺 <|endoftext|> 特殊 token"
    shard_tokens = int(args.shard_gb * (1024 ** 3) / 2)

    val_targets = {"en": round(args.val_tokens * args.en_ratio),
                   "zh": args.val_tokens - round(args.val_tokens * args.en_ratio)}
    flt = DocFilter(args.val_mod, val_targets, args.min_chars, args.max_chars)

    print(f"[cfg] vocab={vocab_size} eos={eos_id} target={args.target_tokens:,} tokens "
          f"en:zh={args.en_ratio:.1f}:{1 - args.en_ratio:.1f} shard={args.shard_gb}GB "
          f"val={args.val_tokens:,}", flush=True)

    train_sink = TokenSink(out, "shard", vocab_size, shard_tokens)
    val_sink = TokenSink(out, "val", vocab_size, None)

    streams = {
        "en": encoded_stream("en", iter_en_raw(args.en_dir), flt, tok, eos_id, vocab_size),
        "zh": encoded_stream("zh", iter_zh_raw(args.zh_src), flt, tok, eos_id, vocab_size),
    }
    iters = {lang: iter(stream) for lang, stream in streams.items()}
    exhausted = {"en": False, "zh": False}
    targets = {"en": args.en_ratio, "zh": 1.0 - args.en_ratio}
    counts = {"en": 0, "zh": 0}
    char_counts = {"en": 0, "zh": 0}
    val_counts = {"en": 0, "zh": 0}
    val_docs = {"en": 0, "zh": 0}
    total = 0
    t0 = time.time()
    last_log = t0

    def log_progress(force: bool = False) -> None:
        nonlocal last_log
        now = time.time()
        if not force and now - last_log < 20:
            return
        elapsed = now - t0
        rate = total / elapsed if elapsed > 0 else 0
        eta = (args.target_tokens - total) / rate / 60 if rate > 0 else 0
        dup_rate = {lang: flt.stats[lang]["dup"] / max(1, flt.stats[lang]["read"])
                    for lang in ("en", "zh")}
        print(f"[build] {total/1e9:.3f}B/{args.target_tokens/1e9:.2f}B ({100*total/args.target_tokens:.1f}%) "
              f"| en {counts['en']/1e9:.3f}B zh {counts['zh']/1e9:.3f}B "
              f"| val {(val_counts['en']+val_counts['zh'])/1e6:.2f}M "
              f"| dup en {dup_rate['en']:.2%} zh {dup_rate['zh']:.2%} "
              f"| {rate/1e3:.0f}k tok/s | ETA {eta:.1f} min", flush=True)
        last_log = now

    def pick_language():
        best, best_deficit = None, None
        for lang in ("en", "zh"):
            if exhausted[lang]:
                continue
            deficit = targets[lang] * (total + 1) - counts[lang]
            if best is None or deficit > best_deficit:
                best, best_deficit = lang, deficit
        return best

    while total < args.target_tokens:
        lang = pick_language()
        if lang is None:
            print("[warn] 两语言流均耗尽，提前结束（未达 target）", flush=True)
            break
        try:
            # 跳过 val 文档（写入 val.bin），直到取到一条 train 文档
            while True:
                kind, ids, nchars, nbytes = next(iters[lang])
                if kind == "train":
                    break
                room = val_targets[lang] - val_counts[lang]
                if room > 0:
                    take = min(len(ids), room)
                    val_sink.add(ids[:take])
                    val_counts[lang] += take
                    val_docs[lang] += 1
                log_progress()
        except StopIteration:
            exhausted[lang] = True
            print(f"[warn] {lang} 语料流耗尽 @ {counts[lang]:,} train tokens", flush=True)
            continue

        take = min(len(ids), args.target_tokens - total)
        train_sink.add(ids[:take])
        counts[lang] += take
        char_counts[lang] += nchars
        total += take
        log_progress()

    train_sink.close()
    val_sink.close()
    elapsed = time.time() - t0
    log_progress(force=True)

    # ---- 换轨冒烟切片（只取第 0 片头部；train_char20m 只换 --data-dir） ----
    smoke = None
    if args.smoke_tokens > 0 and train_sink.files:
        smoke_dir = Path(args.smoke_dir)
        smoke_dir.mkdir(parents=True, exist_ok=True)
        n_train = min(args.smoke_tokens, train_sink.files[0]["tokens"])
        n_val = min(args.smoke_val_tokens, val_sink.total)
        shard0 = np.memmap(out / train_sink.files[0]["name"], dtype=np.uint16, mode="r")
        val_all = np.memmap(out / "val.bin", dtype=np.uint16, mode="r")
        (smoke_dir / "train.bin").write_bytes(np.ascontiguousarray(shard0[:n_train]).tobytes())
        (smoke_dir / "val.bin").write_bytes(np.ascontiguousarray(val_all[:n_val]).tobytes())
        (smoke_dir / "meta.json").write_text(json.dumps({
            "vocab_size": vocab_size,
            "tokenizer": args.tokenizer,
            "note": "BPE 冒烟切片；stats.train_chars/val_chars 实为 token 数（兼容 train_char20m 日志）",
            "stats": {
                "train_chars": int(n_train), "val_chars": int(n_val),
                "train_bin_mb": round(n_train * 2 / 2**20, 1),
                "val_bin_mb": round(n_val * 2 / 2**20, 1),
            },
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        smoke = {"dir": str(smoke_dir), "train_tokens": int(n_train), "val_tokens": int(n_val)}
        print(f"[smoke] 切片 {smoke_dir}: train {n_train:,} tok / val {n_val:,} tok", flush=True)

    # ---- meta + 指纹 ----
    tokenizer_sha = hashlib.sha256(Path(args.tokenizer).read_bytes()).hexdigest()
    lang_stats = {}
    for lang in ("en", "zh"):
        st = flt.stats[lang]
        lang_stats[lang] = {
            **st,
            "train_tokens": counts[lang],
            "train_chars": char_counts[lang],
            "chars_per_token": round(char_counts[lang] / counts[lang], 3) if counts[lang] else None,
            "dup_rate": round(st["dup"] / max(1, st["read"]), 5),
        }
    meta = {
        "vocab_size": vocab_size,
        "eos_id": eos_id,
        "tokenizer": {"path": args.tokenizer, "sha256": tokenizer_sha},
        "mix": {"en_ratio_target": args.en_ratio,
                "en_tokens": counts["en"], "zh_tokens": counts["zh"],
                "total_tokens": total,
                "en_ratio_actual": round(counts["en"] / total, 4) if total else None},
        "sources": {"zh": args.zh_src, "en": args.en_dir},
        "filters": {"min_chars": args.min_chars, "max_chars": args.max_chars,
                    "dedup": "blake2b-64 exact（跨语言共享集合）",
                    "val_split": f"hash % {args.val_mod} == 0，文档级"},
        "stats": lang_stats,
        "val": {"name": "val.bin", "tokens": val_sink.total,
                "en_tokens": val_counts["en"], "zh_tokens": val_counts["zh"],
                "docs": val_docs, "sha256": val_sink.files[0]["sha256"]},
        "shards": train_sink.files,
        "smoke": smoke,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_s": round(elapsed, 1),
        "throughput_tokens_per_s": round(total / elapsed) if elapsed else None,
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [f"{f['sha256']}  {f['name']}" for f in train_sink.files]
    lines += [f"{val_sink.files[0]['sha256']}  {val_sink.files[0]['name']}"]
    (out / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")

    csv_path = Path(args.report_csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "kind", "tokens", "mb", "sha256"])
        for item in train_sink.files:
            w.writerow([item["name"], "train", item["tokens"],
                        round(item["tokens"] * 2 / 2**20, 1), item["sha256"]])
        item = val_sink.files[0]
        w.writerow([item["name"], "val", item["tokens"],
                    round(item["tokens"] * 2 / 2**20, 1), item["sha256"]])

    print("\n[result] 分片清单", flush=True)
    print(f"  {'name':<16} {'tokens':>14} {'MB':>8}  sha256", flush=True)
    for f in train_sink.files + val_sink.files:
        print(f"  {f['name']:<16} {f['tokens']:>14,} {f['tokens']*2/2**20:>8.1f}  {f['sha256'][:16]}…",
              flush=True)
    print(f"[result] 总计 {total:,} train tokens（en {counts['en']/total:.1%} / zh {counts['zh']/total:.1%}）"
          f" + val {val_sink.total:,}（{(val_counts['en']+val_counts['zh'])/val_sink.total:.1%}）", flush=True)
    for lang in ("en", "zh"):
        st = flt.stats[lang]
        print(f"[result] {lang}: read {st['read']:,} docs → short {st['short']:,} / long {st['long']:,} / "
              f"dup {st['dup']:,}（{st['dup']/max(1,st['read']):.2%}）/ val_drop {st['val_dropped']:,} "
              f"→ train {st['train_docs']:,} docs · {counts[lang]:,} tokens · "
              f"{char_counts[lang]/counts[lang]:.2f} chars/token", flush=True)
    print(f"[done] {out}/meta.json · SHA256SUMS · 用时 {elapsed/60:.1f} min · "
          f"{total/elapsed:,.0f} tok/s", flush=True)


if __name__ == "__main__":
    main()