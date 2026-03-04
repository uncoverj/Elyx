"""Start all Elyx services: backend + bot. Run with: python run.py"""
import subprocess
import sys
import os
import time
import httpx

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")
BOT = os.path.join(ROOT, "bot")


def kill_port(port: int):
    try:
        r = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True, capture_output=True, text=True
        )
        for line in r.stdout.splitlines():
            parts = line.split()
            if parts:
                pid = parts[-1]
                if pid.isdigit():
                    subprocess.run(f"taskkill /PID {pid} /F", shell=True, capture_output=True)
    except Exception:
        pass


def wait_backend(url: str, retries: int = 20):
    for i in range(retries):
        try:
            r = httpx.get(f"{url}/health", timeout=3)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        print(f"  Waiting for backend... ({i+1}/{retries})")
        time.sleep(1.5)
    return False


def main():
    print("=== Elyx Launcher ===")

    # Kill anything on port 8000
    print("[1/3] Freeing port 8000...")
    kill_port(8000)
    time.sleep(1)

    # Start backend
    print("[2/3] Starting backend...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=BACKEND,
    )

    if not wait_backend("http://127.0.0.1:8000"):
        print("ERROR: Backend failed to start")
        sys.exit(1)
    print("  Backend ready at http://127.0.0.1:8000")

    # Test keys
    print("[2.5] Testing API keys...")
    try:
        r = httpx.get("http://127.0.0.1:8000/api/test-keys", timeout=10)
        data = r.json()
        for svc, info in data.get("keys", {}).items():
            status = info.get("status", "?")
            icon = "OK" if status == "ok" else "WARN"
            print(f"  [{icon}] {svc}: {status}")
    except Exception as e:
        print(f"  Could not test keys: {e}")

    # Start bot
    print("[3/3] Starting bot...")
    bot_proc = subprocess.Popen(
        [sys.executable, "-m", "app.main"],
        cwd=BOT,
    )

    print("\nAll services running. Press Ctrl+C to stop.\n")
    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        backend_proc.terminate()
        bot_proc.terminate()


if __name__ == "__main__":
    main()
