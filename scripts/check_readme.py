"""Offline checks for the reader entry point, not a knowledge audit."""
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
text = (root / "README.md").read_text(encoding="utf-8")
assert not re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", text), "README has control characters"
assert not re.search(r"^`(?:text|markdown)?$", text, re.M), "Malformed code fence"
assert len(re.findall(r"^```", text, re.M)) % 2 == 0, "Unclosed code fence"
prose = re.sub(r"```.*?```", "", text, flags=re.S)
prose = re.sub(r"`[^`]+`", "", prose)
for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", prose):
    if target.startswith(("http:", "https:", "#", "mailto:")):
        continue
    assert (root / target.split("#")[0]).exists(), f"Missing README target: {target}"
print("README offline checks passed")
