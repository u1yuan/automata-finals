import difflib
import re
from pathlib import Path


def compact(value: str) -> str:
    value = re.sub(r"CS0023: Automata Theory - Comprehensive Reviewer", "", value)
    value = re.sub(r"FEU Institute of Technology\s+Page \d+", "", value)
    value = re.sub(r"\\n===== PAGE \d+ =====\\n", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def parse_final(text: str):
    practice = text.split("## 2. Practice Test Bank (200 Questions)", 1)[1].split(
        "## 3. Comprehensive Answer Key & Explanations", 1
    )[0]
    matches = list(re.finditer(r"(?m)^(\d+)\. (?!Answer:)(.*)$", practice))
    result = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(practice)
        block = practice[match.start():end]
        block = re.sub(r"(?m)^### .*\n+", "", block)
        result[int(match.group(1))] = compact(block)
    return result


def parse_verifier(text: str):
    text = compact(text)
    matches = list(re.finditer(r"(?<!\d)(\d+)\. \1\. ", text))
    result = {}
    for index, match in enumerate(matches):
        number = int(match.group(1))
        if not 1 <= number <= 200 or number in result:
            continue
        later = [item for item in matches[index + 1 :] if int(item.group(1)) == number + 1]
        end = later[0].start() if later else len(text)
        result[number] = compact(text[match.start():end].replace(f"{number}. {number}.", f"{number}."))
    return result


final = parse_final(Path("tmp/pdfs/final-exam_reviewer.cleaned.md").read_text(encoding="utf-8"))
verify = parse_verifier(Path("tmp/pdfs/final-exam_reviewer.verification.txt").read_text(encoding="utf-8"))
for number in range(1, 201):
    left = final.get(number, "")
    right = verify.get(number, "")
    ratio = difflib.SequenceMatcher(None, left, right).ratio()
    if ratio < 0.94:
        print(f"\nQUESTION {number} RATIO {ratio:.3f}")
        print("FINAL :", left.encode("ascii", "backslashreplace").decode())
        print("SOURCE:", right.encode("ascii", "backslashreplace").decode())


def parse_answers(text: str):
    matches = list(re.finditer(r"(?<!\d)(\d+)\. Answer: ", text))
    result = {}
    for index, match in enumerate(matches):
        number = int(match.group(1))
        if not 1 <= number <= 200 or number in result:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result[number] = compact(text[match.start():end])
    return result


final_answers = parse_answers(Path("tmp/pdfs/final-exam_reviewer.cleaned.md").read_text(encoding="utf-8"))
verify_answers = parse_answers(compact(Path("tmp/pdfs/final-exam_reviewer.verification.txt").read_text(encoding="utf-8")))
for number in range(1, 201):
    left = final_answers.get(number, "")
    right = verify_answers.get(number, "")
    ratio = difflib.SequenceMatcher(None, left, right).ratio()
    if ratio < 0.94:
        print(f"\nANSWER {number} RATIO {ratio:.3f}")
        print("FINAL :", left.encode("ascii", "backslashreplace").decode())
        print("SOURCE:", right.encode("ascii", "backslashreplace").decode())


section_ends = {20, 40, 64, 84, 104, 124, 144, 164, 184, 200}
semantic_mismatches = []
for number in range(1, 201):
    if number in section_ends:
        continue
    left = re.sub(r"[\s,]", "", final.get(number, ""))
    right = re.sub(r"[\s,]", "", verify.get(number, ""))
    ratio = difflib.SequenceMatcher(None, left, right).ratio()
    if ratio < 0.985:
        semantic_mismatches.append((number, round(ratio, 3)))
print("SEMANTIC QUESTION MISMATCHES", semantic_mismatches)
