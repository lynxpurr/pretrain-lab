"""app.py — Day 7: 本地聊天 demo（Gradio → Ollama）

前置：
  1) Ollama 用户级服务（系统服务无权限写模型目录）：
     OLLAMA_MODELS=$HOME/.ollama/models OLLAMA_HOST=127.0.0.1:11435 ollama serve
  2) 导入量化模型（Q4_K_M）：
     OLLAMA_HOST=127.0.0.1:11435 ollama create pretrain-lab-sft-v2-q4 -f out/Modelfile-sft-v2-q4
启动：
  .venv-pre/bin/python -I tools/app.py --model pretrain-lab-sft-v2-q4 --port 7860
"""
from __future__ import annotations

import argparse
import os

import gradio as gr
import requests


def history_to_messages(history) -> list[dict]:
    """兼容 Gradio 4/5（[user, assistant] 对）与 6（role/content dict）。"""
    out: list[dict] = []
    if not history:
        return out
    for item in history:
        if isinstance(item, dict) and "role" in item:
            out.append({"role": item["role"], "content": item.get("content") or ""})
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            u, a = item
            if u:
                out.append({"role": "user", "content": u})
            if a:
                out.append({"role": "assistant", "content": a})
    return out


def make_chat(host: str, model: str, temperature: float, top_p: float, max_new: int):
    def chat(message: str, history) -> str:
        messages = history_to_messages(history)
        messages.append({"role": "user", "content": message})
        try:
            r = requests.post(
                f"{host}/api/chat",
                json={"model": model, "messages": messages, "stream": False,
                      "options": {"temperature": temperature, "top_p": top_p,
                                  "num_ctx": 1024, "num_predict": max_new,
                                  "stop": ["<|im_end|>"]}},
                timeout=180,
            )
            r.raise_for_status()
            return (r.json().get("message") or {}).get("content", "").strip() or "（空回复）"
        except Exception as e:  # demo 端把错误显示给用户，避免白屏
            return f"[demo error] {type(e).__name__}: {e}\n请确认 Ollama 服务与模型名：{host} / {model}"
    return chat


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=os.environ.get("OLLAMA_URL", "http://127.0.0.1:11435"))
    ap.add_argument("--model", default="pretrain-lab-sft-v2-q4")
    ap.add_argument("--port", type=int, default=7860)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--top-p", type=float, default=0.9)
    ap.add_argument("--max-new", type=int, default=200)
    args = ap.parse_args()

    demo = gr.ChatInterface(
        make_chat(args.host, args.model, args.temperature, args.top_p, args.max_new),
        title="pretrain-lab · 140M 中英小模型",
        description=("从零预训练 3B token + SFT v2 的 140M 模型（Ollama 本地推理，Q4 量化）。"
                     "能力有限：事实知识贫乏、数学不可靠，长回答可能复读；评测分数与 demo 采样参数分开声明。"),
        examples=[
            "你是谁？",
            "请用一句话解释什么是机器学习。",
            "What is the capital of France?",
            "7 乘以 6 等于多少？只回答数字。",
            "请告诉我 2027 年世界杯的冠军是谁。",
        ],
    )
    demo.launch(server_name="0.0.0.0", server_port=args.port, share=False)


if __name__ == "__main__":
    main()