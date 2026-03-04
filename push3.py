import os, subprocess

ROOT = r"c:\Users\tt964\Desktop\Elyx"
GIT = r"C:\Program Files\Git\bin\git.exe"

os.remove(os.path.join(ROOT, "push2.py")) if os.path.exists(os.path.join(ROOT, "push2.py")) else None

def git(*args):
    r = subprocess.run([GIT] + list(args), cwd=ROOT, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if out: print(out)
    return r.returncode

git("add", "-A")
git("commit", "-m", "Update run.py: auto-start tunnel, clean launcher")
rc = git("push", "origin", "main")
print("Pushed!" if rc == 0 else "Push failed")

# Self-delete
os.remove(__file__)
