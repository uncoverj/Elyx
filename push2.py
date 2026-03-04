import os, subprocess, sys

ROOT = r"c:\Users\tt964\Desktop\Elyx"

# Find git executable
GIT_PATHS = [
    r"C:\Program Files\Git\bin\git.exe",
    r"C:\Program Files (x86)\Git\bin\git.exe",
    r"C:\Users\tt964\AppData\Local\Programs\Git\bin\git.exe",
]
git = None
for p in GIT_PATHS:
    if os.path.exists(p):
        git = p
        break
if not git:
    import shutil
    git = shutil.which("git") or "git"

print(f"Using git: {git}")

def run(args):
    r = subprocess.run([git] + args, cwd=ROOT, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if out:
        print(out)
    return r.returncode

run(["add", "-A"])
rc = run(["commit", "-m", "Fix API key validation + Valorant error handling"])
if rc not in (0, 1):  # 1 = nothing to commit
    print("Commit failed")
    sys.exit(1)
rc = run(["push", "origin", "main"])
if rc == 0:
    print("\nPushed to GitHub!")
else:
    print("\nPush failed")
