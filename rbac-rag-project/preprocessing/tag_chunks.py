import json
import yaml
from pathlib import Path

IN_FILE = Path("../processed/chunks.jsonl")
OUT_FILE = Path("../processed/chunks_tagged.jsonl")
QA_FILE = Path("../processed/qa_summary.json")

# load mapping
with open("../mappings/role_document_mapping.yaml", "r", encoding="utf-8") as f:
    role_map = yaml.safe_load(f)

def get_department(filename):
    fname = filename.lower()
    for dept, conf in role_map.items():
        pats = conf.get("patterns") if isinstance(conf, dict) else conf
        if not pats:
            continue
        for p in pats:
            if p.lower() in fname:
                return dept
    return "Employees"

counts = {}
out_rows = []

with open(IN_FILE, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)

        # FIXED CALL
        dept = get_department(obj["file_name"])
        obj["department"] = dept

        # accessible roles
        if dept == "C-Level":
            obj["accessible_roles"] = ["C-Level", "Admin"]
        elif dept == "Employees":
            obj["accessible_roles"] = ["Employees", "Admin"]
        else:
            obj["accessible_roles"] = [dept, "Admin"]

        out_rows.append(obj)
        counts[dept] = counts.get(dept, 0) + 1

# write tagged chunks
with open(OUT_FILE, "w", encoding="utf-8") as f:
    for row in out_rows:
        f.write(json.dumps(row) + "\n")

# write QA summary
with open(QA_FILE, "w", encoding="utf-8") as f:
    json.dump({"total_chunks": len(out_rows), "counts": counts}, f, indent=2)

print("Tagging complete!")
print("Wrote:", OUT_FILE)
print("Summary:", counts)
