import os, subprocess

ROOT = r"c:\Users\tt964\Desktop\Elyx"
GIT = r"C:\Program Files\Git\bin\git.exe"

def git(*args):
    r = subprocess.run([GIT] + list(args), cwd=ROOT, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if out: print(out)
    return r.returncode

git("add", "-A")
git("commit", "-m", "Complete webapp redesign: dark theme, tabbar, mock data")
rc = git("push", "origin", "main")
print("Pushed!" if rc == 0 else "Push failed")

os.remove(__file__)
