#!/bin/bash
# Start the unified Qwen server (chat + review) and open the web UI.
#
# The default model is now the Qwen3.8-27B GGUF, served by llama.cpp's
# llama-server. This script will start llama-server for you if it is not
# already running, then start the FastAPI app that talks to it.
#
# The previous MLX models are unchanged and still selectable, e.g.
#   ./start_server.sh --model 35b

# Resolve the project root from this script's own location, so the
# folder can be renamed or moved without editing anything.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR/app"
DEFAULT_PORT=8080
DEFAULT_HOST="127.0.0.1"

# --- Local settings, then models ------------------------------------------
# local.env is sourced before anything is worked out, so a setting there
# survives a restart started from the browser: the app server re-launches this
# script, and whatever was exported in a shell is long gone. See
# local.env.example.
if [[ -f "$SCRIPT_DIR/local.env" ]]; then
  # Exported, not merely set: local.env uses ': "${VAR:=value}"' lines, which
  # create shell variables that a child process never sees. Settings the
  # Python app reads (QWEN_REVIEW_STORE, LLAMA_MODEL_DIRS, QWEN_REVIEW_THINKING
  # and others) were therefore silently ignored when they came from local.env.
  set -a
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/local.env"
  set +a
fi

# shellcheck disable=SC1091
source "$SCRIPT_DIR/scripts/model_aliases.sh"

DEFAULT_MODEL="$QWEN38_27B_GGUF"

# managed: this launcher starts llama-server for a GGUF model (the default).
# external: you start llama-server yourself; set LLAMA_SERVER_URL and this
# launcher only connects to it. See local.env.example.
LLAMA_SERVER_MODE="$(printf '%s' "${LLAMA_SERVER_MODE:-managed}" | tr '[:upper:]' '[:lower:]')"
case "$LLAMA_SERVER_MODE" in
  managed|external) ;;
  *) echo "LLAMA_SERVER_MODE must be 'managed' or 'external' (got: $LLAMA_SERVER_MODE)" >&2; exit 1 ;;
esac

# QWEN_MODEL in local.env is the documented way to choose the model. This
# launcher used to ignore it and always fell back to the built-in path, which
# does not exist on most machines.
if [[ "$LLAMA_SERVER_MODE" == "external" ]]; then
  MODEL="${QWEN_MODEL:-llama-server}"
else
  MODEL="$(resolve_model "${QWEN_MODEL:-$DEFAULT_MODEL}")" || exit 1
fi
PORT="$DEFAULT_PORT"
HOST="$DEFAULT_HOST"
OPEN_BROWSER=1

# --- llama-server (used only for GGUF models) -----------------------------
LLAMA_PORT="${LLAMA_SERVER_PORT:-8081}"
LLAMA_HOST="${LLAMA_SERVER_HOST:-127.0.0.1}"
LLAMA_CTX="${LLAMA_SERVER_CTX:-32768}"
LLAMA_NGL="${LLAMA_SERVER_NGL:-99}"
LLAMA_BIN="${LLAMA_SERVER_BIN:-llama-server}"
LLAMA_LOG="$SCRIPT_DIR/logs/llama-server.log"
LLAMA_PID_FILE="$SCRIPT_DIR/run/llama-server.pid"
KEEP_LLAMA=0

print_usage() {
  cat <<EOF
Local LLM Server

Usage:
  ./start_server.sh [options]

Options:
  --model MODEL       Model alias, .gguf path, or Hugging Face repo ID.
  --port PORT         FastAPI server port (default: $DEFAULT_PORT).
  --host HOST         Bind address (default: $DEFAULT_HOST).
  --llama-port PORT   llama-server port for GGUF models (default: $LLAMA_PORT).
  --ctx N             llama-server context size (default: $LLAMA_CTX).
  --keep-llama        Leave llama-server running after this script exits.
  --no-open           Do not open the browser after startup.
  --list-models       Show built-in model aliases.
  -h, --help          Show this help.

Examples:
  ./start_server.sh                          # Qwen3.8-27B GGUF (default)
  ./start_server.sh --port 8090
  ./start_server.sh --model 35b --port 8090  # back to the MLX 35B model
  ./start_server.sh --model gemma4
  ./start_server.sh --model /path/to/other.gguf

Default:
  $DEFAULT_MODEL
EOF
}

list_models() {
  cat <<EOF
Installed model aliases:
  qwen38, 27b-gguf, gguf      -> $QWEN38_27B_GGUF
                                 (llama.cpp / llama-server)
  35b, 35b-4bit, qwen35       -> $QWEN35_4BIT   (MLX)
  27b, 27b-6bit, qwen27       -> $QWEN27_6BIT   (MLX)
  gemma4, gemma4-26b,
  gemma4-26b-it               -> $GEMMA4_26B_A4B_IT_4BIT   (MLX)

A full Hugging Face repo ID or an absolute path to a .gguf file is also
accepted unchanged.
EOF
}


while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      if [[ -z "${2:-}" ]]; then
        echo "Missing value for --model" >&2
        exit 1
      fi
      MODEL="$(resolve_model "$2")" || exit 1
      shift 2
      ;;
    --port)
      if [[ -z "${2:-}" ]]; then
        echo "Missing value for --port" >&2
        exit 1
      fi
      PORT="$2"
      shift 2
      ;;
    --host)
      if [[ -z "${2:-}" ]]; then
        echo "Missing value for --host" >&2
        exit 1
      fi
      HOST="$2"
      shift 2
      ;;
    --llama-port)
      if [[ -z "${2:-}" ]]; then
        echo "Missing value for --llama-port" >&2
        exit 1
      fi
      LLAMA_PORT="$2"
      shift 2
      ;;
    --ctx)
      if [[ -z "${2:-}" ]]; then
        echo "Missing value for --ctx" >&2
        exit 1
      fi
      LLAMA_CTX="$2"
      shift 2
      ;;
    --keep-llama)
      KEEP_LLAMA=1
      shift
      ;;
    --no-open)
      OPEN_BROWSER=0
      shift
      ;;
    --list-models)
      list_models
      exit 0
      ;;
    -h|--help)
      print_usage
      echo ""
      list_models
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Run ./start_server.sh --help for usage." >&2
      exit 1
      ;;
  esac
done

# Free the app port only if it is held by this application's own server.py.
# This used to kill whatever held the port, which could take down an
# unrelated program that happened to use it.
for APP_PORT_PID in $(lsof -ti "tcp:$PORT" -sTCP:LISTEN 2>/dev/null); do
  if ps -p "$APP_PORT_PID" -o command= 2>/dev/null | grep -q "app/server.py"; then
    echo "Stopping the previous app server on port $PORT (pid $APP_PORT_PID)."
    kill "$APP_PORT_PID" 2>/dev/null || true
  else
    echo "Port $PORT is in use by pid $APP_PORT_PID ($(ps -p "$APP_PORT_PID" -o comm= 2>/dev/null || echo unknown))," >&2
    echo "which is not this application. Refusing to stop it; choose another port with --port." >&2
    exit 1
  fi
done
for _ in $(seq 1 20); do
  lsof -ti "tcp:$PORT" -sTCP:LISTEN > /dev/null 2>&1 || break
  sleep 0.5
done

source "$SCRIPT_DIR/.venv/bin/activate"

# Check every start-up dependency before starting. This used to install
# unpinned fastapi/uvicorn when fastapi was absent and checked nothing else.
if ! python "$SCRIPT_DIR/scripts/check_install.py" --quiet; then
  echo "Install the pinned requirements, then start again:" >&2
  echo "  $SCRIPT_DIR/.venv/bin/python -m pip install -r $SCRIPT_DIR/requirements.txt" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# For a GGUF model, make sure llama-server is up before starting the app.
# ---------------------------------------------------------------------------
LLAMA_URL="http://$LLAMA_HOST:$LLAMA_PORT"
LLAMA_PID=""

llama_http_code() {
  local code
  code="$(curl -s -o /dev/null -m 2 -w '%{http_code}' "$1" 2>/dev/null || true)"
  printf '%s' "${code:-000}"
}

# Ready means HTTP 200. While llama.cpp is loading a model /health answers 503,
# and the previous check (any answer at all) declared a loading server ready.
is_llama_up() {
  [[ "$(llama_http_code "$LLAMA_URL/health")" == "200" ]] \
    || [[ "$(llama_http_code "$LLAMA_URL/props")" == "200" ]]
}

# Something is answering HTTP on the port, ready or not.
is_llama_listening() {
  [[ "$(llama_http_code "$LLAMA_URL/health")" != "000" ]]
}

# The pid of the llama-server this launcher or scripts/qwen_service.sh
# started, if the pid file names a live llama-server; empty otherwise.
managed_llama_pid() {
  local pid=""
  [[ -f "$LLAMA_PID_FILE" ]] && pid="$(cat "$LLAMA_PID_FILE" 2>/dev/null || true)"
  if [[ -n "$pid" ]] && ps -p "$pid" -o command= 2>/dev/null | grep -q llama-server; then
    printf '%s' "$pid"
  fi
  return 0
}

stop_llama() {
  local pid
  if [[ -n "$LLAMA_PID" && "$KEEP_LLAMA" -eq 0 ]]; then
    # A model switch from the browser replaces the process, so the one to
    # stop is whichever the pid file now names, not necessarily LLAMA_PID.
    pid="$(managed_llama_pid)"
    [[ -z "$pid" ]] && kill -0 "$LLAMA_PID" 2>/dev/null && pid="$LLAMA_PID"
    if [[ -n "$pid" ]]; then
      echo ""
      echo "Stopping llama-server (pid $pid)..."
      kill "$pid" 2>/dev/null || true
      rm -f "$LLAMA_PID_FILE"
    fi
  fi
}

# Which model does the llama-server on this port actually have loaded?
#
# Reusing a running server is normally what you want: the model stays resident
# between runs. But it was reused without checking which model it held, so
# switching model from the web UI restarted the app server with the new path
# while llama-server carried on serving the old one. The report header takes
# its Model line from the app server, so it named a model that had not written
# a word of the review. Any comparison between two GGUF models was silently
# invalid. Empty means the server did not say, and then reuse is reported as
# unverified rather than claimed as a match.
served_llama_model() {
  local raw=""
  raw="$(curl -s -m 3 "$LLAMA_URL/v1/models" 2>/dev/null \
         | tr ',' '\n' \
         | sed -n 's/.*"id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
         | head -1)"
  if [[ -z "$raw" ]]; then
    raw="$(curl -s -m 3 "$LLAMA_URL/props" 2>/dev/null \
           | tr ',' '\n' \
           | sed -n 's/.*"model_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
           | head -1)"
  fi
  if [[ -n "$raw" ]]; then
    basename "$raw"
  fi
  return 0
}

# Stop the llama-server on the port so a different model can be loaded, but
# only if the pid file shows that this launcher or scripts/qwen_service.sh
# started it. There used to be a fallback that killed whatever process was
# listening on the port, which could stop a server someone else started.
stop_served_llama() {
  local pid
  pid="$(managed_llama_pid)"
  [[ -n "$pid" ]] || return 1

  kill "$pid" 2>/dev/null || true
  for _ in $(seq 1 20); do
    is_llama_listening || { rm -f "$LLAMA_PID_FILE"; return 0; }
    sleep 0.5
  done
  kill -9 "$pid" 2>/dev/null || true
  sleep 1
  if is_llama_listening; then
    return 1
  fi
  rm -f "$LLAMA_PID_FILE"
  return 0
}

if [[ "$LLAMA_SERVER_MODE" == "external" ]]; then
  # Connect only. Model identity comes from the server, and the app offers no
  # restart for a process it does not manage.
  export LLAMA_SERVER_URL="${LLAMA_SERVER_URL:-$LLAMA_URL}"
  export QWEN_LLM_BACKEND="llama-server"
  export LLAMA_SERVER_MODE="external"
  if [[ "$(llama_http_code "$LLAMA_SERVER_URL/health")" == "000" ]]; then
    echo "WARNING: no llama-server is answering at $LLAMA_SERVER_URL."
    echo "The app will start and report it as unreachable until you start one."
  fi
  BACKEND_LABEL="external llama-server @ $LLAMA_SERVER_URL"
elif [[ "$MODEL" == *.gguf ]]; then
  if [[ ! -f "$MODEL" ]]; then
    echo "Model file not found: $MODEL" >&2
    exit 1
  fi

  if ! command -v "$LLAMA_BIN" > /dev/null 2>&1; then
    cat >&2 <<EOF
llama-server was not found on PATH (looked for: $LLAMA_BIN).

Install or update llama.cpp, for example:
  brew install llama.cpp      # or: brew upgrade llama.cpp

Each model needs a build that knows its architecture: qwen35 for the 27B,
qwen4exp for Flash-Next. If llama-server loads but reports an unknown
architecture, the build does not have that model. Point LLAMA_SERVER_BIN at a
build that does, and put it in local.env so the setting survives a restart
started from the browser -- see local.env.example.

To use the previous MLX model instead, which needs no llama-server at all:
  ./start_server.sh --model 35b
EOF
    exit 1
  fi

  if is_llama_listening && ! is_llama_up; then
    printf "A llama-server on %s is still loading a model; waiting" "$LLAMA_URL"
    for _ in $(seq 1 300); do
      is_llama_up && break
      printf "."
      sleep 2
    done
    echo ""
  fi

  NEEDS_LLAMA_START=1
  if is_llama_up; then
    SERVED_MODEL="$(served_llama_model)"
    WANTED_MODEL="$(basename "$MODEL")"
    if [[ -z "$SERVED_MODEL" ]]; then
      echo "Reusing the llama-server already listening on $LLAMA_URL."
      echo "It did not report which model it has loaded, so that was not checked."
      NEEDS_LLAMA_START=0
    elif [[ "$SERVED_MODEL" == "$WANTED_MODEL" ]]; then
      echo "Reusing the llama-server already listening on $LLAMA_URL ($SERVED_MODEL)"
      NEEDS_LLAMA_START=0
    else
      echo "llama-server on $LLAMA_URL has $SERVED_MODEL loaded, but $WANTED_MODEL"
      echo "was asked for. Stopping it so the requested model can be loaded."
      if ! stop_served_llama; then
        cat >&2 <<EOF

The llama-server on port $LLAMA_PORT was not stopped. Either it was not
started by this launcher or scripts/qwen_service.sh (no matching pid file),
so it is not safe to stop, or it would not exit. It is serving $SERVED_MODEL,
so a review started now would be written by that model whatever this
launcher was asked for.

Stop it where it was started, use another port (--llama-port), or connect to
it as it is with LLAMA_SERVER_MODE=external.
EOF
        exit 1
      fi
    fi
  fi

  if [[ "$NEEDS_LLAMA_START" -eq 1 ]]; then
    mkdir -p "$SCRIPT_DIR/logs"
    echo "Starting llama-server on $LLAMA_URL (log: $LLAMA_LOG)"

    # Vision needs the projector in memory, and the per-review selector in the
    # browser can only turn vision on if it is. scripts/qwen_service.sh loads
    # one whenever it sits beside the model; this launcher did not, so a
    # restart from the web UI silently lost vision. Set QWEN_LOAD_MMPROJ=0 to
    # keep it out.
    LLAMA_VISION_ARGS=()
    if [[ "${QWEN_LOAD_MMPROJ:-1}" == "1" ]]; then
      MMPROJ_FILE="$(ls "$(dirname "$MODEL")"/*mmproj*.gguf 2>/dev/null | head -1)"
      if [[ -n "$MMPROJ_FILE" ]]; then
        LLAMA_VISION_ARGS=(--mmproj "$MMPROJ_FILE" --image-min-tokens 1024)
        echo "Vision available: $(basename "$MMPROJ_FILE")"
      else
        echo "No projector beside this model, so vision is unavailable."
      fi
    fi

    # Flags this model needs, and flags this machine needs. The first travel
    # with the model so that choosing it in the browser brings them along;
    # local.env cannot make a setting conditional on the model chosen.
    LLAMA_MODEL_ARGS=( $(model_extra_args "$MODEL") )
    LLAMA_EXTRA_ARGS=( ${LLAMA_SERVER_EXTRA_ARGS:-} )
    if [[ ${#LLAMA_MODEL_ARGS[@]} -gt 0 || ${#LLAMA_EXTRA_ARGS[@]} -gt 0 ]]; then
      echo "Extra llama-server flags: ${LLAMA_MODEL_ARGS[*]-} ${LLAMA_EXTRA_ARGS[*]-}"
    fi

    "$LLAMA_BIN" \
      --model "$MODEL" \
      --host "$LLAMA_HOST" \
      --port "$LLAMA_PORT" \
      --ctx-size "$LLAMA_CTX" \
      --n-gpu-layers "$LLAMA_NGL" \
      --jinja \
      ${LLAMA_VISION_ARGS[@]+"${LLAMA_VISION_ARGS[@]}"} \
      ${LLAMA_MODEL_ARGS[@]+"${LLAMA_MODEL_ARGS[@]}"} \
      ${LLAMA_EXTRA_ARGS[@]+"${LLAMA_EXTRA_ARGS[@]}"} \
      > "$LLAMA_LOG" 2>&1 &
    LLAMA_PID=$!
    # Recorded so that a model switch from the browser, and qwen_service.sh,
    # can recognise this process as one they may stop.
    mkdir -p "$SCRIPT_DIR/run"
    echo "$LLAMA_PID" > "$LLAMA_PID_FILE"
    trap stop_llama EXIT INT TERM

    printf "Loading the model"
    for _ in $(seq 1 300); do
      if is_llama_up; then
        echo " ready."
        break
      fi
      if ! kill -0 "$LLAMA_PID" 2>/dev/null; then
        echo ""
        echo "llama-server exited during startup. Last lines of the log:" >&2
        tail -n 25 "$LLAMA_LOG" >&2
        exit 1
      fi
      printf "."
      sleep 2
    done

    if ! is_llama_up; then
      echo ""
      echo "llama-server did not become ready in time. See $LLAMA_LOG" >&2
      exit 1
    fi
  fi

  export LLAMA_SERVER_URL="$LLAMA_URL"
  export QWEN_LLM_BACKEND="llama-server"
  # Managed only if this launcher or the service started the process; a
  # server reused from elsewhere is external to the app.
  if [[ -n "$(managed_llama_pid)" ]]; then
    export LLAMA_SERVER_MODE="managed"
  else
    export LLAMA_SERVER_MODE="external"
  fi
  BACKEND_LABEL="llama.cpp @ $LLAMA_URL ($LLAMA_SERVER_MODE)"
else
  export QWEN_LLM_BACKEND="mlx"
  BACKEND_LABEL="MLX (in-process)"
fi

# Passed on so that a model switch requested from the browser starts the new
# model with the same port and context size. A full restart of the app (needed
# to change between MLX and GGUF) belongs to scripts/qwen_service.sh.
export LLAMA_SERVER_HOST="$LLAMA_HOST" LLAMA_SERVER_PORT="$LLAMA_PORT" LLAMA_SERVER_CTX="$LLAMA_CTX"
export QWEN_SERVICE_MANAGED=0

echo "============================================"
echo "  Local LLM Server"
echo "  Model:   $(basename "$MODEL")"
echo "  Backend: $BACKEND_LABEL"
echo "  Host:    $HOST"
echo "  Port:    $PORT"
echo "  UI:      http://localhost:$PORT"
echo "============================================"
echo ""
echo "Press Ctrl+C to stop."
echo ""

if [[ "$OPEN_BROWSER" -eq 1 ]]; then
  # Open browser after a short delay; the model is already loaded by now
  # when using llama-server, so this can be shorter than it used to be.
  (sleep 3 && open "http://localhost:$PORT" 2>/dev/null) &
fi

python "$APP_DIR/server.py" --model "$MODEL" --port "$PORT" --host "$HOST"
