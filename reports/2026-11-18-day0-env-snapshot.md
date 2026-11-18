# Day 0 环境快照 — 2026-11-18（.venv-pre 建立证据）

## 验证记录（判据：HANDOFF §3-1，D-07）

> 补记（2026-11-18 晚）：HANDOFF 已重构，Day 0 清单原 §3 表并入新 §3「已完成摘要」；本报告即该批次判据的原始证据，不再依赖 HANDOFF 章节号。

```
python: 3.12.13 (uv-managed, ~/.local/share/uv/python)
torch: 2.11.0+cu128
cuda: True
device: NVIDIA GeForce RTX 5070 Ti | capability: (12, 0)
sm_120 in arch list: True
bf16 matmul 2048x2048 @ cuda: OK（mean -0.0196533203125）
mem free 13.4GiB / total 15.5GiB（laya-triage 常驻 ~1.8G 在位）
```

## 版本锁（uv pip list 关键件）

```
datasets                                 5.2.0
matplotlib                               3.11.2
numpy                                    2.5.5
pyyaml                                   6.0.3
safetensors                              0.8.0
tensorboard                              2.21.0
tokenizers                               0.23.3
torch                                    2.11.0+cu128
tqdm                                     4.70.1
transformers                             5.23.0
triton                                   3.6.0
wandb                                    0.31.0
```

## 装法（nl2fem runbook §3 → finetune-lab PLAN §9 平移，换 venv 名 .venv-pre）

```bash
export PATH="$HOME/.local/bin:$PATH" UV_HTTP_TIMEOUT=600 UV_TORCH_BACKEND=cu128
ALI=https://mirrors.aliyun.com/pypi/simple/  PTW=https://mirrors.aliyun.com/pytorch-wheels/cu128/
uv venv .venv-pre --python=3.12 --seed   # D-07: uv 托管解释器，不链 /usr/bin
uv pip install --python .venv-pre/bin/python torch numpy tqdm tensorboard wandb transformers datasets tokenizers matplotlib pyyaml --index-url "$ALI" --find-links "$PTW"
```

## 参考实现落位（Day 0-3，D-08）

- minimind @ `233d00f`（~/projects/minimind，数据文件现行名 = pretrain_t2t(_mini)/sft_t2t(_mini)，见其 README L122-423）
- nanoGPT @ `3adf61e`（~/projects/nanoGPT）

## §2 复现检查（2026-11-18 全绿）

| 项 | 值 |
|---|---|
| git | develop 干净，与 origin 同步 |
| GPU 空闲 | 13998 MiB（与锚点一致） |
| 磁盘 | / 余 2.3T |
| tmux | /usr/bin/tmux 在位 |
