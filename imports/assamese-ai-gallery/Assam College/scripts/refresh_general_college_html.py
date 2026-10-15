"""Keep the standalone HTML views aligned with general_colleges.csv."""

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "general_colleges.csv").open(newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    columns = reader.fieldnames
    rows = list(reader)


def embed(path, tag, selection):
    html = path.read_text(encoding="utf-8")
    data = json.dumps({"columns": columns, "rows": selection}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    pattern = rf'(<script id="{tag}" type="application/json">).*?(</script>)'
    html, changed = re.subn(pattern, lambda match: match.group(1) + data + match.group(2), html, count=1, flags=re.S)
    assert changed == 1, f"Missing data script in {path}"
    path.write_text(html, encoding="utf-8")


dashboard = ROOT / "general_colleges_dashboard.html"
embed(dashboard, "directoryData", rows)
html = dashboard.read_text(encoding="utf-8")
html = re.sub(r"<span>\d+ institutions</span>", f"<span>{len(rows)} institutions</span>", html, count=1)
html = re.sub(r"<span>\d+ districts</span>", f"<span>{len({r['District'] for r in rows})} districts</span>", html, count=1)
html = re.sub(r"<span>\d+ fields including academic review</span>", f"<span>{len(columns)} fields including academic review</span>", html, count=1)
dashboard.write_text(html, encoding="utf-8")

missing = [r for r in rows if not r["Departments"].strip()]
embed(ROOT / "general_colleges_missing_departments.html", "sourceData", missing)
print(f"Refreshed dashboard ({len(rows)} colleges) and manual review ({len(missing)} colleges)")
