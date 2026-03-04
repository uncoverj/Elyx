import re

env_path = r"c:\Users\tt964\Desktop\Elyx\.env"

with open(env_path, "r") as f:
    content = f.read()

content = re.sub(r"HENRIK_API_KEY=.*", "HENRIK_API_KEY=HDEV-addbd95e-b174-4a9d-95dd-f9d0850d9411", content)
content = re.sub(r"FACEIT_API_KEY=.*", "FACEIT_API_KEY=99c9beba-57ee-482f-aa38-a85810d40e31", content)

with open(env_path, "w") as f:
    f.write(content)

print("Updated .env:")
for line in content.splitlines():
    if "API_KEY" in line or "WEBAPP" in line or "BACKEND_URL" in line:
        print(" ", line)
