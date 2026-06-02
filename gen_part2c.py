
import sys
fpath = "e:/project/ClaudeCodeWs/C006_CQDigital_worker/digital-worker/backend/app/seeds/seed_all.py"

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

anchor = "        print("Audit tables seeded successfully.")"
suffix = ""
"""
# (content will be filled below)
"""

with open(fpath, "a", encoding="utf-8") as f:
    f.write(suffix)
