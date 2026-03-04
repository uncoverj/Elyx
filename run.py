"""
Start all Elyx services: backend + localtunnel + bot.
Usage: python run.py

After starting, copy the tunnel URL shown and set it in Vercel:
  Settings -> Environment Variables -> NEXT_PUBLIC_BACKEND_URL = <tunnel_url>
Then redeploy Vercel (without build cache).
"""
import subprocess
import sys
import os
import time
import re
import threading
import httpx

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")
BOT = os.path.join(ROOT, "bot")

_procs: list[subprocess.Popen] = []


def kill_port(port: int):
    try:
        r = subprocess.run(
            f"netstat -ano | findstr :{port}",
            shell=True, capture_output=True, text=True,
        )
        for line in r.stdout.splitlines():
            parts = line.split()
            if parts:
                pid = parts[-1]
                if pid.isdigit() and pid != "0":
                    subprocess.run(f"taskkill /PID {pid} /F", shell=True, capture_output=True)
    except Exception:
        pass


def wait_backend(url: str, retries: int = 25) -> bool:
    for i in range(retries):
        try:
            r = httpx.get(f"{url}/health", timeout=3)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1.5)
    return False


def start_tunnel(port: int) -> tuple[subprocess.Popen, str]:
    """Start localtunnel and return (process, public_url)."""
    proc = subprocess.Popen(
        ["npx", "localtunnel", "--port", str(port)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, shell=True,
    )
    # Read lines until we find the URL (up to 30s)
    url = ""
    deadline = time.time() + 30
    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.2)
            continue
        m = re.search(r"(https://[a-z0-9\-]+\.loca\.lt)", line)
        if m:
            url = m.group(1)
            break
    return proc, url


def main():
    print("=" * 50)
    print("  Elyx Launcher — backend + tunnel + bot")
    print("=" * 50)

    # 1. Free port 8000
    print("\n[1/4] Freeing port 8000...")
    kill_port(8000)
    time.sleep(1)

    # 2. Start backend
    print("[2/4] Starting backend...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "127.0.0.1", "--port", "8000"],
        cwd=BACKEND,
    )
    _procs.append(backend_proc)

    if not wait_backend("http://127.0.0.1:8000"):
        print("ERROR: Backend failed to start. Check logs above.")
        sys.exit(1)
    print("  ✓ Backend ready at http://127.0.0.1:8000")

    # Test API keys
    try:
        r = httpx.get("http://127.0.0.1:8000/api/test-keys", timeout=10)
        keys = r.json().get("keys", {})
        for svc, info in keys.items():
            st = info.get("status", "?")
            icon = "✓" if st == "ok" else "✗"
            print(f"  [{icon}] {svc.upper()} key: {st}")
    except Exception:
        pass

    # 3. Start localtunnel
    print("\n[3/4] Starting localtunnel for port 8000...")
    tunnel_proc, tunnel_url = start_tunnel(8000)
    _procs.append(tunnel_proc)

    if tunnel_url:
        print(f"\n{'='*50}")
        print(f"  PUBLIC URL: {tunnel_url}")
        print(f"{'='*50}")
        print(f"\n  ➡  Go to Vercel Dashboard → Settings → Environment Variables")
        print(f"     Set: NEXT_PUBLIC_BACKEND_URL = {tunnel_url}")
        print(f"     Then: Deployments → Redeploy (uncheck 'use cache')")
        print(f"\n{'='*50}\n")
    else:
        print("  WARNING: Could not get tunnel URL. Is 'npx' (Node.js) installed?")
        print("  Run manually: npx localtunnel --port 8000")

    # 4. Start bot
    print("[4/4] Starting bot...")
    bot_proc = subprocess.Popen(
        [sys.executable, "-m", "app.main"],
        cwd=BOT,
    )
    _procs.append(bot_proc)
    print("  ✓ Bot started (@Elyxxbot)")

    print("\nAll services running. Press Ctrl+C to stop all.\n")
    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down all services...")
        for p in _procs:
            try:
                p.terminate()
            except Exception:
                pass


if __name__ == "__main__":
    main()
