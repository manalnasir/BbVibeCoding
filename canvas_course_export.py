
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from canvasapi import Canvas

load_dotenv()

CANVAS_URL = os.getenv("CANVAS_URL")
CANVAS_TOKEN = os.getenv("CANVAS_TOKEN")
COURSE_ID = int(os.getenv("COURSE_ID"))

canvas = Canvas(CANVAS_URL, CANVAS_TOKEN)
course = canvas.get_course(COURSE_ID)

EXPORT_DIR = Path("course_export")
EXPORT_DIR.mkdir(exist_ok=True)

def attrs(obj):
    return getattr(obj, "attributes", dict(getattr(obj, "__dict__", {})))

def save(name, data):
    with open(EXPORT_DIR / name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

export = {
    "exported_at": datetime.utcnow().isoformat() + "Z",
    "course": attrs(course),
    "modules": [],
    "pages": [],
    "assignments": [],
    "discussions": [],
    "quizzes": [],
    "files": [],
    "folders": [],
    "rubrics": [],
    "sections": [],
    "users": [],
    "errors": []
}

for m in course.get_modules():
    d = attrs(m)
    try:
        d["items"] = [attrs(i) for i in m.get_module_items()]
    except Exception as e:
        d["items_error"] = str(e)
    export["modules"].append(d)

for p in course.get_pages():
    try:
        export["pages"].append(attrs(course.get_page(p.url)))
    except Exception as e:
        export["errors"].append({"page": getattr(p,"url",""), "error": str(e)})

for a in course.get_assignments():
    export["assignments"].append(attrs(a))

try:
    for d in course.get_discussion_topics():
        x = attrs(d)
        try:
            x["entries"] = [attrs(e) for e in d.get_entries()]
        except Exception:
            pass
        export["discussions"].append(x)
except Exception as e:
    export["errors"].append({"discussions": str(e)})

try:
    for q in course.get_quizzes():
        x = attrs(q)
        try:
            x["questions"] = [attrs(qq) for qq in q.get_questions()]
        except Exception:
            pass
        export["quizzes"].append(x)
except Exception as e:
    export["errors"].append({"quizzes": str(e)})

for f in course.get_files():
    export["files"].append(attrs(f))
for f in course.get_folders():
    export["folders"].append(attrs(f))
for r in course.get_rubrics():
    export["rubrics"].append(attrs(r))
for s in course.get_sections():
    export["sections"].append(attrs(s))
try:
    for u in course.get_users():
        export["users"].append(attrs(u))
except Exception:
    pass

save("course_export.json", export)
print("Export complete.")
