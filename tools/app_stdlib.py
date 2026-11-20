"""app_stdlib.py — Day 7: 零依赖本地聊天 demo（stdlib HTTP + Ollama API）

用途：Gradio 安装受网络影响时的保底方案；功能等价于 tools/app.py（多轮对话 + 本地 URL）。
启动：
  .venv-pre/bin/python -I tools/app_stdlib.py --model pretrain-lab-sft-v2e-q8 --port 7860
然后浏览器打开 http://127.0.0.1:7860
"""
from __future__ import annotations

import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import requests

HTML = r"""<!doctype html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>pretrain-lab · 140M 小模型</title>
<style>
  :root{--bg:#0f1115;--card:#171a21;--line:#2a2f3a;--fg:#e8ebf0;--muted:#9aa4b2;--accent:#5b8cff}
  *{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,Segoe UI,Roboto,"Noto Sans SC",sans-serif}
  .wrap{max-width:860px;margin:0 auto;height:100vh;display:flex;flex-direction:column}
  header{padding:18px 20px 10px;border-bottom:1px solid var(--line)}
  h1{font-size:17px;margin:0 0 4px} .sub{color:var(--muted);font-size:12.5px}
  #chat{flex:1;overflow:auto;padding:18px 20px;display:flex;flex-direction:column;gap:12px}
  .msg{max-width:86%;padding:10px 13px;border-radius:12px;white-space:pre-wrap;word-break:break-word}
  .user{align-self:flex-end;background:#23324f;border:1px solid #2f466f}
  .bot{align-self:flex-start;background:var(--card);border:1px solid var(--line)}
  .meta{color:var(--muted);font-size:11px;margin-bottom:3px}
  .composer{display:flex;gap:8px;padding:12px 20px 16px;border-top:1px solid var(--line)}
  textarea{flex:1;resize:none;height:52px;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:10px;padding:10px 12px;font:inherit}
  button{background:var(--accent);color:#fff;border:0;border-radius:10px;padding:0 18px;font:inherit;cursor:pointer}
  button:disabled{opacity:.5;cursor:not-allowed}
  .examples{display:flex;gap:6px;flex-wrap:wrap;padding:0 20px 10px}
  .examples button{background:transparent;color:var(--muted);border:1px solid var(--line);font-size:12px;padding:5px 9px}
</style></head><body>
<div class="wrap">
  <header><h1>pretrain-lab · 140M 中英小模型</h1>
  <div class="sub">从零预训练 3B token + SFT v2 · Ollama 本地量化推理 · 能力有限：事实知识贫乏、数学不可靠，长回答可能复读</div></header>
  <div id="chat"></div>
  <div class="examples">
    <button onclick="ex('你是谁？')">你是谁？</button>
    <button onclick="ex('请用一句话解释什么是机器学习。')">一句话解释 ML</button>
    <button onclick="ex('What is the capital of France?')">Capital of France</button>
    <button onclick="ex('7 乘以 6 等于多少？只回答数字。')">只回答数字</button>
    <button onclick="ex('请告诉我 2027 年世界杯的冠军是谁。')">2027 世界杯</button>
  </div>
  <div class="composer">
    <textarea id="q" placeholder="输入问题，Enter 发送（Shift+Enter 换行）"></textarea>
    <button id="send" onclick="send()">发送</button>
  </div>
</div>
<script>
const chat=document.getElementById('chat'), q=document.getElementById('q'), sendBtn=document.getElementById('send');
let history=[];
function add(role,text){const d=document.createElement('div');d.className='msg '+role;
  d.innerHTML='<div class="meta">'+(role==='user'?'你':'模型')+'</div>';d.appendChild(document.createTextNode(text));chat.appendChild(d);chat.scrollTop=chat.scrollHeight;return d;}
function ex(t){q.value=t;q.focus();}
async function send(){
  const text=q.value.trim(); if(!text) return;
  q.value=''; add('user',text); history.push({role:'user',content:text});
  sendBtn.disabled=true; const pending=add('bot','思考中…');
  try{
    const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:text,history:history.slice(0,-1)})});
    const j=await r.json(); const ans=j.answer||('[error] '+(j.error||'unknown'));
    pending.remove(); add('bot',ans); history.push({role:'assistant',content:ans});
  }catch(e){pending.remove(); add('bot','[demo error] '+e);}
  sendBtn.disabled=false; q.focus();
}
q.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}});
add('bot','你好，我是 pretrain-lab 训练的 140M 小模型。问我点什么吧（能力有限，长回答可能复读）。');
</script></body></html>"""


def make_handler(host: str, model: str, temperature: float, top_p: float, max_new: int,
                 num_gpu: int = -1):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def _send(self, code: int, body: bytes, ctype: str):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if urlparse(self.path).path in ("/", "/index.html"):
                self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
            elif urlparse(self.path).path == "/health":
                self._send(200, b'{"ok":true}', "application/json")
            else:
                self._send(404, b"not found", "text/plain; charset=utf-8")

        def do_POST(self):
            if urlparse(self.path).path != "/api/chat":
                self._send(404, b"not found", "text/plain")
                return
            n = int(self.headers.get("Content-Length", 0))
            try:
                data = json.loads(self.rfile.read(n) or b"{}")
                messages = list(data.get("history") or [])
                messages.append({"role": "user", "content": data.get("message", "")})
                opts = {"temperature": temperature, "top_p": top_p,
                        "num_ctx": 1024, "num_predict": max_new, "stop": ["<|im_end|>"]}
                if num_gpu >= 0:
                    opts["num_gpu"] = num_gpu
                r = requests.post(
                    f"{host}/api/chat",
                    json={"model": model, "messages": messages, "stream": False, "options": opts},
                    timeout=180,
                )
                r.raise_for_status()
                ans = (r.json().get("message") or {}).get("content", "").strip()
                self._send(200, json.dumps({"answer": ans}, ensure_ascii=False).encode("utf-8"),
                           "application/json; charset=utf-8")
            except Exception as e:
                self._send(200, json.dumps({"answer": "", "error": f"{type(e).__name__}: {e}"},
                                           ensure_ascii=False).encode("utf-8"),
                           "application/json; charset=utf-8")
    return Handler


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=os.environ.get("OLLAMA_URL", "http://127.0.0.1:11435"))
    ap.add_argument("--model", default="pretrain-lab-sft-v2e-q8")
    ap.add_argument("--port", type=int, default=7860)
    ap.add_argument("--temperature", type=float, default=0.3)
    ap.add_argument("--top-p", type=float, default=0.9)
    ap.add_argument("--max-new", type=int, default=200)
    ap.add_argument("--num-gpu", type=int, default=-1, help="-1 = Ollama 默认；0 = 强制 CPU（训练期间验证用）")
    ap.add_argument("--bind", default="0.0.0.0")
    args = ap.parse_args()
    srv = ThreadingHTTPServer((args.bind, args.port),
                              make_handler(args.host, args.model, args.temperature, args.top_p,
                                           args.max_new, args.num_gpu))
    print(f"[demo] http://127.0.0.1:{args.port}  →  Ollama {args.host} · model={args.model}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()