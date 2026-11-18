#!/bin/bash
# Start llama.cpp's llama-server with a GGUF model and leave it running.
#
# This is one way to run an externally managed server: the app connects to it
# (LLAMA_SERVER_MODE=external) but never starts, stops or restarts it. Any
# llama-server you start yourself works the same way. The default model is
# the Qwen example path; pass --model or set LLAMA_MODEL for another.
#
# Usage:
#   ./start_llama_server.sh --model /path/to/model.gguf   # foreground, Ctrl+C
#   ./start_llama_server.sh --port 8081 --ctx 32768

HF_HUB="${HF_HUB_CACHE:-$HOME/.cache/huggingface/hub}"
MODEL="${LLAMA_MODEL:-$HF_HUB/models--unsloth--Qwen3.8-27B-GGUF/snapshots/4ca720788d1e01f1bff70c033e0d0028fd02e502/Qwen3.8-27B-UD-Q4_K_XL.gguf}"

HOST="${LLAMA_SERVER_HOST:-127.0.0.1}"
PORT="${LLAMA_SERVER_PORT:-8081}"
CTX="${LLAMA_SERVER_CTX:-32768}"
NGL="${LLAMA_SERVER_NGL:-99}"
BIN="${LLAMA_SERVER_BIN:-llama-server}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --host)  HOST="$2";  shift 2 ;;
    --port)  PORT="$2";  shift 2 ;;
    --ctx)   CTX="$2";   shift 2 ;;
    --ngl)   NGL="$2";   shift 2 ;;
    -h|--help)
      sed -n '2,13p' "$0"
      exit 0
      ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ ! -f "$MODEL" ]]; then
  echo "Model file not found: $MODEL" >&2
  exit 1
fi

if ! command -v "$BIN" > /dev/null 2>&1; then
  echo "llama-server not found on PATH (looked for: $BIN)." >&2
  echo "Install or update llama.cpp:  brew install llama.cpp" >&2
  exit 1
fi

echo "Model: $(basename "$MODEL")"
echo "URL:   http://$HOST:$PORT"
echo ""
echo "To use it from the app, put these in local.env (see local.env.example):"
echo "  LLAMA_SERVER_MODE=external"
echo "  LLAMA_SERVER_URL=http://$HOST:$PORT"
echo "To switch models, stop this server and start it again with --model."
echo ""

# --jinja is required: it makes llama.cpp apply the chat template embedded in
# the GGUF, which is what honours enable_thinking=false and suppresses the
# model's reasoning block.
exec "$BIN" \
  --model "$MODEL" \
  --host "$HOST" \
  --port "$PORT" \
  --ctx-size "$CTX" \
  --n-gpu-layers "$NGL" \
  --jinja
