import hashlib
import json
import re
from pathlib import Path

import fitz


root = Path.cwd()
pdf_path = root / "final-exam_reviewer.pdf"
markdown_path = root / "final-exam_reviewer.md"
spec_path = root / "final-exam_reviewer_conversion_spec.md"
assets_dir = root / "final-exam_reviewer_assets"

text = markdown_path.read_text(encoding="utf-8")
practice = text.split("## 2. Practice Test Bank (200 Questions)", 1)[1].split(
    "## 3. Comprehensive Answer Key & Explanations", 1
)[0]
answers = text.split("## 3. Comprehensive Answer Key & Explanations", 1)[1].split(
    "## Appendix Images", 1
)[0]

question_matches = list(re.finditer(r"(?m)^(\d+)\. (?!Answer:)", practice))
question_numbers = [int(match.group(1)) for match in question_matches]
assert question_numbers == list(range(1, 201))
for index, match in enumerate(question_matches):
    end = question_matches[index + 1].start() if index + 1 < len(question_matches) else len(practice)
    block = practice[match.start():end]
    choices = re.findall(r"(?m)^([A-D])\. ", block)
    assert choices == ["A", "B", "C", "D"], (match.group(1), choices)

answer_numbers = [int(value) for value in re.findall(r"(?m)^(\d+)\. Answer:", answers)]
assert answer_numbers == list(range(1, 201))

expected_sections = [
    *(f"1.{index}" for index in range(1, 11)),
    *(f"2.{index}" for index in range(1, 11)),
    *(f"3.{index}" for index in range(1, 11)),
]
actual_sections = re.findall(r"(?m)^### (\d+\.\d+)\b", text)
assert actual_sections == expected_sections, actual_sections

defects = {
    "replacement_character": "�" in text,
    "running_header": "CS0023: Automata Theory - Comprehensive Reviewer" in text,
    "running_footer": bool(re.search(r"FEU Institute of Technology|Page \d+", text)),
    "duplicated_question_number": bool(re.search(r"(?m)^(\d+)\. \1\. ", text)),
    "markdown_table_artifact": bool(re.search(r"(?m)^\|", text)),
}
assert not any(defects.values()), defects

expected_links = [
    f"final-exam_reviewer_assets/page-{page}-image-{index}.png"
    for page, count in ((37, 3), (38, 3), (39, 2))
    for index in range(1, count + 1)
]
actual_links = re.findall(r"!\[[^]]*\]\(([^)]+)\)", text)
assert actual_links == expected_links, actual_links

asset_paths = sorted(assets_dir.glob("*.png"))
assert [path.relative_to(root).as_posix() for path in asset_paths] == sorted(expected_links)
dimensions = {}
for relative in expected_links:
    path = root / relative
    assert path.is_file() and path.stat().st_size > 0
    assert path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    pixmap = fitz.Pixmap(str(path))
    assert pixmap.width > 0 and pixmap.height > 0
    dimensions[path.name] = [pixmap.width, pixmap.height]

document = fitz.open(pdf_path)
assert len(document) == 39
page_image_counts = [len(document[index].get_images(full=True)) for index in (36, 37, 38)]
assert page_image_counts == [3, 3, 2], page_image_counts

assert spec_path.is_file() and spec_path.stat().st_size > 0
assert markdown_path.stat().st_size > 0

symbol_counts = {symbol: text.count(symbol) for symbol in ("×", "δ", "ε", "→", "∗", "λ", "Γ", "∆")}
assert all(symbol_counts.values()), symbol_counts

result = {
    "pdf_pages": len(document),
    "pdf_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
    "questions": len(question_numbers),
    "choices": 800,
    "answers": len(answer_numbers),
    "sections": len(actual_sections),
    "appendix_page_image_counts": page_image_counts,
    "assets": len(asset_paths),
    "asset_dimensions": dimensions,
    "links_resolved": len(actual_links),
    "defects": defects,
    "symbol_counts": symbol_counts,
}
print(json.dumps(result, indent=2, ensure_ascii=True))
