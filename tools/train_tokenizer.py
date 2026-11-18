"""train_tokenizer.py — Day 2: 训练 32k 中英 BPE tokenizer（D-03）

语料采样（确定性、流式）：
  zh = minimind pretrain_t2t.jsonl 头部 ~300MB；en = fineweb-edu sample-10BT 头部 ~300MB；
  两语言各再顺延 ~5MB 作**留出评测集**（不参与训练，只量压缩率）。
Tokenizer：HF tokenizers 的 ByteLevel BPE——初始字母表 = 256 个字节，任意 UTF-8 都可编码、
  无 OOV；特殊 token = <|endoftext|>(0) / <|im_start|>(1) / <|im_end|>(2)（Day 5 SFT 复用）。
产出：data/tokenizer-32k/{tokenizer.json, vocab.json, merges.txt, meta.json}；
  压缩率对拍 minimind 现成 6.4k tokenizer（同留出文本），CSV 落 reports/。

用法（仓库根目录）：`.venv-pre/bin/python -I tools/train_tokenizer.py 2>&1 | tee logs/day2-tokenizer-<stamp>.log`
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from pathlib import Path

from tokenizers import Tokenizer, decoders, models, pre_tokenizers, trainers

SPECIAL_TOKENS = ["<|endoftext|>", "<|im_start|>", "<|im_end|>"]


def iter_zh(path: str):
    """逐行产出 pretrain_t2t.jsonl 的 text 字段。"""
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                doc = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = doc.get("text", "")
            if text:
                yield str(text)


def iter_en(parquet_dir: str):
    """按文件名序、row group 序流式产出 fineweb-edu parquet 的 text 字段。"""
    import pyarrow.parquet as pq

    for p in sorted(Path(parquet_dir).glob("*.parquet")):
        pf = pq.ParquetFile(p)
        for i in range(pf.metadata.num_row_groups):
            col = pf.read_row_group(i, columns=["text"]).column(0)
            for text in col.to_pylist():
                if text:
                    yield text


def sample_split(iterable, sample_bytes: int, val_bytes: int):
    """顺序采样：前 sample_bytes 作文本训练集，随后 val_bytes 作留出评测集。

    返回 (train_texts, val_texts, stats)。按 UTF-8 字节计预算（与磁盘/编码成本对齐）。
    """
    train: list[str] = []
    val: list[str] = []
    got_train = got_val = 0
    n_seen = 0
    for text in iterable:
        n_seen += 1
        n = len(text.encode("utf-8"))
        if got_train < sample_bytes:
            train.append(text)
            got_train += n
        elif got_val < val_bytes:
            val.append(text)
            got_val += n
        else:
            break
    stats = {
        "docs_seen": n_seen,
        "train_docs": len(train),
        "train_bytes": got_train,
        "val_docs": len(val),
        "val_bytes": got_val,
    }
    return train, val, stats


def build_tokenizer(texts: list[str], vocab_size: int) -> Tokenizer:
    tok = Tokenizer(models.BPE())
    tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tok.decoder = decoders.ByteLevel()
    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        show_progress=True,
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
        special_tokens=SPECIAL_TOKENS,
    )
    tok.train_from_iterator(texts, trainer=trainer)
    return tok


def measure(tok: Tokenizer, texts: list[str], batch: int = 1000) -> dict:
    """编码留出文本，统计 token 数与压缩率。"""
    n_tokens = n_chars = n_bytes = 0
    for i in range(0, len(texts), batch):
        chunk = texts[i:i + batch]
        encs = tok.encode_batch(chunk, add_special_tokens=False)
        n_tokens += sum(len(e.ids) for e in encs)
        n_chars += sum(len(t) for t in chunk)
        n_bytes += sum(len(t.encode("utf-8")) for t in chunk)
    return {
        "docs": len(texts),
        "chars": n_chars,
        "bytes": n_bytes,
        "tokens": n_tokens,
        "chars_per_token": round(n_chars / n_tokens, 3),
        "bytes_per_token": round(n_bytes / n_tokens, 3),
    }


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zh-src", default="data/raw/minimind_dataset/pretrain_t2t.jsonl")
    ap.add_argument("--en-dir", default="data/raw/fineweb-edu/sample/10BT")
    ap.add_argument("--out-dir", default="data/tokenizer-32k")
    ap.add_argument("--vocab-size", type=int, default=32000)
    ap.add_argument("--sample-mb", type=float, default=300.0, help="每语言训练 tokenizer 的采样量")
    ap.add_argument("--val-mb", type=float, default=5.0, help="每语言留出压缩率评测量")
    ap.add_argument("--minimind-tokenizer", default=str(Path.home() / "projects/minimind/model/tokenizer.json"))
    ap.add_argument("--report-csv", default="reports/2026-11-18-day2-tokenizer.csv")
    args = ap.parse_args()

    sample_bytes = int(args.sample_mb * 1e6)
    val_bytes = int(args.val_mb * 1e6)
    t0 = time.time()

    # ---- 1. 采样 ----
    print(f"[sample] zh ← {args.zh_src}（{args.sample_mb}MB + 留出 {args.val_mb}MB）", flush=True)
    zh_train, zh_val, zh_stats = sample_split(iter_zh(args.zh_src), sample_bytes, val_bytes)
    print(f"[sample] zh: train {zh_stats['train_docs']:,} docs / {zh_stats['train_bytes']/1e6:.1f}MB "
          f"· heldout {zh_stats['val_docs']:,} docs / {zh_stats['val_bytes']/1e6:.1f}MB", flush=True)

    print(f"[sample] en ← {args.en_dir}（{args.sample_mb}MB + 留出 {args.val_mb}MB）", flush=True)
    en_train, en_val, en_stats = sample_split(iter_en(args.en_dir), sample_bytes, val_bytes)
    print(f"[sample] en: train {en_stats['train_docs']:,} docs / {en_stats['train_bytes']/1e6:.1f}MB "
          f"· heldout {en_stats['val_docs']:,} docs / {en_stats['val_bytes']/1e6:.1f}MB", flush=True)

    # ---- 2. 训练 BPE（中英混采，一个词表共享） ----
    print(f"[train] BPE vocab={args.vocab_size}（ByteLevel, 256 字节兜底，specials={SPECIAL_TOKENS}）", flush=True)
    tok = build_tokenizer(zh_train + en_train, args.vocab_size)
    assert tok.get_vocab_size() == args.vocab_size, \
        f"词表未训满：{tok.get_vocab_size()} ≠ {args.vocab_size}（语料不足或 min_frequency 配置错）"
    for i, s in enumerate(SPECIAL_TOKENS):
        assert tok.token_to_id(s) == i, f"特殊 token 编号漂移：{s} → {tok.token_to_id(s)}"
    print(f"[train] 完成：{tok.get_vocab_size():,} tokens（{time.time() - t0:.1f}s）", flush=True)

    # ---- 3. 落盘 ----
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tok.save(str(out / "tokenizer.json"))
    tok.model.save(str(out))  # 附出 vocab.json + merges.txt（可读/可审计）
    tok_json_sha = sha256_file(out / "tokenizer.json")
    sums = [f"{sha256_file(out / name)}  {name}"
            for name in ("tokenizer.json", "vocab.json", "merges.txt")]
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")

    # ---- 4. 压缩率评测（留出集，ours vs minimind 6400） ----
    probes = {"zh": zh_val, "en": en_val}
    ours = {lang: measure(tok, texts) for lang, texts in probes.items()}
    ref_tok = None
    ref = {}
    ref_path = Path(args.minimind_tokenizer)
    if ref_path.exists():
        ref_tok = Tokenizer.from_file(str(ref_path))
        ref = {lang: measure(ref_tok, texts) for lang, texts in probes.items()}
    else:
        print(f"[warn] minimind tokenizer 不在位：{ref_path}，跳过对拍", flush=True)

    # 往返自检：任意 UTF-8（emoji/生僻字/零宽字符）必须 byte-level 无损。
    # 注意 decode() 默认 skip_special_tokens=True 会吞特殊 token——探针不含特殊字面量，另测特殊 token。
    probe = "中文English mixed: 你好，世界! 🌍👩‍🚀 — ﬀ ①𠀀\n第二行\t"
    ids = tok.encode(probe).ids
    assert max(ids) < args.vocab_size
    assert tok.decode(ids, skip_special_tokens=False) == probe, "ByteLevel 往返不自洽（归一化/解码器配置错）"
    special_ids = [tok.token_to_id(s) for s in SPECIAL_TOKENS]
    assert tok.decode(special_ids, skip_special_tokens=False) == "".join(SPECIAL_TOKENS), \
        "特殊 token 解码不自洽"
    print(f"[check] 往返自检通过；probe → {len(ids)} tokens；specials → {special_ids}", flush=True)

    # ---- 5. 证据 + meta ----
    rows = []
    for lang in ("zh", "en"):
        o = ours[lang]
        rows.append({"tokenizer": f"ours-{args.vocab_size}", "lang": lang, **o})
        if ref:
            r = ref[lang]
            rows.append({"tokenizer": f"minimind-{ref_tok.get_vocab_size()}", "lang": lang, **r,
                         "ours_over_ref_tokens": round(o["tokens"] / r["tokens"], 4)})

    csv_path = Path(args.report_csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["tokenizer", "lang", "docs", "chars", "bytes", "tokens",
              "chars_per_token", "bytes_per_token", "ours_over_ref_tokens"]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    meta = {
        "vocab_size": args.vocab_size,
        "special_tokens": {s: tok.token_to_id(s) for s in SPECIAL_TOKENS},
        "model": "BPE + ByteLevel pre_tokenizer（initial_alphabet = 256 bytes）",
        "sample": {"zh": zh_stats, "en": en_stats,
                   "sample_mb_per_lang": args.sample_mb, "heldout_mb_per_lang": args.val_mb},
        "compression_heldout": ours,
        "vs_minimind": ref,
        "tokenizer_json_sha256": tok_json_sha,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_s": round(time.time() - t0, 1),
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n[result] 留出集压缩率（chars/token 越高越好）", flush=True)
    print(f"  {'tokenizer':<16} {'lang':<4} {'chars/token':>12} {'bytes/token':>12} {'tokens':>12}", flush=True)
    for row in rows:
        print(f"  {row['tokenizer']:<16} {row['lang']:<4} {row['chars_per_token']:>12} "
              f"{row['bytes_per_token']:>12} {row['tokens']:>12,}", flush=True)
    if ref:
        for lang in ("zh", "en"):
            ratio = ours[lang]["tokens"] / ref[lang]["tokens"]
            print(f"  [对拍] {lang}: 同文 token 数 ours/ref = {ratio:.3f}（32k vs 6.4k 词表，"
                  f"预期 < 1；若 > 1.3 或 < 0.5 查配置）", flush=True)
    print(f"[done] 落位 {out}/（tokenizer.json sha256={tok_json_sha[:16]}…）· csv {csv_path}", flush=True)


if __name__ == "__main__":
    main()