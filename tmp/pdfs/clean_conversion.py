import re
from pathlib import Path


SOURCE = Path("tmp/pdfs/final-exam_reviewer.raw.md")
OUTPUT = Path("tmp/pdfs/final-exam_reviewer.cleaned.md")


def is_separator(line: str) -> bool:
    if not (line.startswith("|") and line.endswith("|")):
        return False
    cells = [cell.strip() for cell in line[1:-1].split("|")]
    return bool(cells) and all(not cell or re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def flatten_table_row(line: str) -> str:
    cells = [cell.strip() for cell in line[1:-1].split("|")]
    parts: list[str] = []
    for index, cell in enumerate(cells):
        if cell:
            parts.append(cell)
            continue
        previous = next((value for value in reversed(cells[:index]) if value), "")
        following = next((value for value in cells[index + 1 :] if value), "")
        # A literal set-builder/union bar becomes an empty table cell in
        # MarkItDown's sparse PDF table representation.
        if previous.endswith("{x") and following.startswith("x "):
            parts.append("|")
    return " ".join(parts)


raw_lines = SOURCE.read_text(encoding="utf-8").splitlines()
lines: list[str] = []
for raw in raw_lines:
    line = raw.strip()
    if not line or is_separator(line):
        continue
    if line.startswith("|") and line.endswith("|"):
        line = flatten_table_row(line)
    line = re.sub(r"\s+", " ", line).strip()
    if not line:
        continue
    if re.search(r"CS0023:\s+Automata\s+Theory\s+-\s+Comprehensive\s+Reviewer", line):
        continue
    if re.search(r"FEU\s+Institute\s+of Technology.*Page\s+\d+$", line):
        continue
    lines.append(line)


headings = {
    "1 Topical Concept Summaries": "## 1. Topical Concept Summaries",
    "2 Practice Test Bank (200 Questions)": "## 2. Practice Test Bank (200 Questions)",
    "3 Comprehensive Answer Key & Explanations": "## 3. Comprehensive Answer Key & Explanations",
    "APPENDICES": "## Appendix Images",
}


def normalize_line(line: str) -> str:
    line = headings.get(line, line)
    line = re.sub(r"^(\d+)\.\s+\1\.\s+", r"\1. ", line)
    line = re.sub(r"^(\d+\.\d+)\s+\d+\.\s+", r"\1 ", line)
    if re.match(r"^(?:2|3)\.\d+\s+\d+[–-]\d+\.\s+", line):
        line = re.sub(r"^(\d+\.\d+)\s+(\d+[–-]\d+)\.\s+", r"### \1 \2. ", line)
    elif re.match(r"^1\.\d+\s+", line):
        line = "### " + line
    return line


lines = [normalize_line(line) for line in lines]

# Repair a handful of unambiguous extraction joins without changing wording.
exact_replacements = {
    "CS0023: Automata Theory and Formal Languages": "# CS0023: Automata Theory and Formal Languages",
    "Comprehensive Final Exam Reviewer & Test Bank": "## Comprehensive Final Exam Reviewer & Test Bank",
}
lines = [exact_replacements.get(line, line) for line in lines]


def is_block_start(line: str) -> bool:
    return bool(
        line.startswith("#")
        or re.match(r"^\d+\.\s+", line)
        or re.match(r"^[A-D]\.\s+", line)
        or re.match(r"^\d+\.\s+Answer:\s+", line)
        or line in {"Computer Science Department", "3TSY2526"}
    )


blocks: list[str] = []
for line in lines:
    if is_block_start(line):
        blocks.append(line)
        continue
    if not blocks:
        blocks.append(line)
        continue
    previous = blocks[-1]
    if previous.startswith("#") or previous in {"Computer Science Department", "3TSY2526"}:
        blocks.append(line)
        continue
    if previous.endswith("-") and line and line[0].islower():
        blocks[-1] = previous[:-1] + line
    else:
        blocks[-1] = previous + " " + line


text = "\n\n".join(blocks)
text = re.sub(r"\b(\d+)\.\s+\1\.\s+", r"\1. ", text)
text = re.sub(r"[ \t]+", " ", text)
text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"

# Source-confirmed repairs for words split or merged by PDF column extraction.
word_repairs = {
    "statesymbol": "state-symbol",
    "Kleenestar": "Kleene star ",
    "Precedencematters": "Precedence matters",
    "starbindsstrongest": "star binds strongest",
    "concatenationcomesnext": "concatenation comes next",
    "andunionis": "and union is",
    "TheChomskyhierarchyclassifiesgrammarsandtheircorrespondingmachinesfromType-3upto": "The Chomsky hierarchy classifies grammars and their corresponding machines from Type-3 up to",
    "Regulargrammarscorrespondtofiniteautomata": "Regular grammars correspond to finite automata",
    "preservingthelanguage,usuallyexceptfortheemptystringifhandledseparately": "preserving the language, usually except for the empty string if handled separately",
    "Leftrecursion iseliminatedtomaketop-downparsingandnormal-formconversioneasier": "Left recursion is eliminated to make top-down parsing and normal-form conversion easier",
    "InChomskyNormal Form": "In Chomsky Normal Form",
    "ThemaindistinctionbetweenMooreandMealymachinesiswhetheroutputsdepend": "The main distinction between Moore and Mealy machines is whether outputs depend",
    "A.Thefirstcomponentmustcomefromthefirstsetandthesecondcomponent": "A. The first component must come from the first set and the second component",
    "B.ADFAacceptsonlyiftheinputisexhaustedandthefinalstateisaccepting": "B. A DFA accepts only if the input is exhausted and the final state is accepting",
    "A.Nondeterminismmeansoneinputsymbolcanleadtoseveralpossiblemoves": "A. Nondeterminism means one input symbol can lead to several possible moves",
    "B.Themachinerequiresatleastoneinputsymbolalongtheleadingandtrailing": "B. The machine requires at least one input symbol along the leading and trailing",
    "B.Acommonconversionusestheoutputofthestateenteredbythattransition": "B. A common conversion uses the output of the state entered by that transition",
    "A.EachdistinctoutputonincomingtransitionsoftenrequiresadistinctMoore": "A. Each distinct output on incoming transitions often requires a distinct Moore",
    "A.Unreachablesymbolscanneverappearinaderivationfromthestartsymbol": "A. Unreachable symbols can never appear in a derivation from the start symbol",
    "A.CNFisastandardnormalformfortheoreticalproofsandparsingalgorithms": "A. CNF is a standard normal form for theoretical proofs and parsing algorithms",
    "righthand": "right-hand",
    "onestep": "one-step",
    "BimesA": "B × A",
    "Q 1 imesQ 2": "Q1 × Q2",
}
for old, new in word_repairs.items():
    text = text.replace(old, new)
text = text.replace("both components must be 1 accepting", "both components must be accepting")
text = text.replace("{x x", "{x | x")
text = re.sub(r",(?=[A-Za-z0-9εδλΣΓ])", ", ", text)
text = re.sub(r"\s*×\s*", " × ", text)
text = re.sub(r"\bq\s+([0-9])\b", r"q\1", text)
text = re.sub(r"\bL\s+([12])\b", r"L\1", text)


question_repairs = {
    26: """26. Which expression correctly defines the extended transition function of a DFA?

A. δ : Q × Σ → Q

B. δ : Q × Σ → 2^Q

C. δ : Q → Σ

D. δ : Q × Σ → Q × ∆""",
    5: """5. Let L1 = {a, ab} and L2 = {b, ε}. Which string is in L1L2?

A. ab

B. ba

C. aa

D. bb""",
    8: """8. Which set-builder notation describes all strings over {0, 1} with exactly two 1s?

A. {x | x ∈ {0, 1}∗ and x has exactly two 1s}

B. {x | x ∈ {0, 1}∗ and x has at least two 1s}

C. {x | x ∈ {0, 1}∗ and x ends in 1}

D. {x | x ∈ {0, 1}∗ and x begins with 1}""",
    11: """11. Let L1 = {0, 1} and L2 = {a, b}. Which string is in L1L2?

A. 0a

B. ab

C. 1a

D. All of the above""",
    14: """14. Which set-builder notation describes all binary strings that contain at least one 0?

A. {x | x ∈ {0, 1}∗ and x contains at least one 0}

B. {x | x ∈ {0, 1}∗ and x contains exactly one 0}

C. {x | x ∈ {0, 1}∗ and x starts with 0}

D. {x | x ∈ {0, 1}∗ and x ends with 1}""",
    16: """16. If L1 = {ε, a} and L2 = {b}, which string is in L1L2?

A. b

B. a

C. ε

D. abb""",
    18: """18. Which set-builder notation matches all strings over {a, b} that end in aa?

A. {x | x ∈ {a, b}∗ and x ends in aa}

B. {x | x ∈ {a, b}∗ and x begins in aa}

C. {x | x ∈ {a, b}∗ and x has exactly two as}

D. {x | x ∈ {a, b}∗ and x contains no b}""",
    22: """22. If δ(q0, 0) = q1 and δ(q1, 1) = q2, what is δ∗(q0, 01)?

A. q0

B. q1

C. q2

D. {q2}""",
    31: """31. If δ(q0, 1) = q1 and δ(q1, 0) = q0, what is δ∗(q0, 10)?

A. q0

B. q1

C. {q0, q1}

D. ∅""",
    32: """32. Which statement about a DFA transition graph is correct?

A. Edges are undirected

B. Each edge represents an ordered move on one symbol

C. Every accepting state has no outgoing edges

D. Loops are forbidden""",
    33: """33. What does the notation δ∗ represent in automata theory?

A. The set of all states

B. The extended transition function on strings

C. The output function of a Mealy machine

D. The stack alphabet of a PDA""",
    36: """36. In the formal DFA definition (Q, Σ, δ, q0, F), the set F denotes

A. the set of final states

B. the alphabet

C. the transition relation

D. the stack symbols""",
    50: """50. If p ε−→ r and r ε−→ s, then s belongs to the ε-closure of

A. only s

B. only r

C. p

D. the alphabet""",
    53: """53. Machine 7 is an ε-NFA built using Thompson’s construction. Its underlying regex structure is most consistent with

A. a(a|b)∗b

B. a∗b∗

C. (ab)∗

D. b(a|b)∗a""",
    67: """67. Which string belongs to (0|1)∗1?

A. 101

B. 000

C. ε

D. 1110""",
    68: """68. The regex (x|y)∗ describes

A. exactly one symbol

B. zero or more symbols each equal to x or y

C. only the string xy

D. all strings of length 2""",
    69: """69. Which pattern describes all strings over {a, b} that end in ab?

A. ab∗

B. (a|b)∗ab

C. a∗b∗

D. a|b""",
    71: """71. The regex 0(1|0)1 generates

A. 001

B. 010

C. 011

D. 101""",
    72: """72. Which of the following is equivalent to (ab)∗?

A. All strings of a’s then b’s

B. Repetitions of the block ab

C. Strings ending in a

D. Strings with at least one a""",
    73: """73. In regex syntax, a union symbol | means

A. concatenation

B. choice between alternatives

C. repetition

D. intersection""",
    74: """74. Which string is NOT in (0|1)∗0?

A. 10

B. 1010

C. 111

D. 000""",
    76: """76. Which string is generated by (a|b)a(a|b)?

A. aaa

B. bab

C. bbb

D. baaab""",
    77: """77. Which pattern matches all strings containing at least one 1?

A. 0∗1 followed by anything

B. 1∗

C. (0|1)∗1(0|1)∗

D. 0∗1∗""",
    78: """78. The regex (ab|ba) accepts

A. exactly the strings ab and ba

B. all strings of length 2

C. only strings beginning with a

D. the empty string""",
    79: """79. Which string is in a∗b(a|b)∗?

A. bbb

B. aababa

C. aaaa

D. ε""",
    80: """80. Which of these is a valid regular expression under the usual precedence rules?

A. a|bc∗

B. a|b

C. ab|

D. ∗ab""",
    81: """81. The expression (0|1)(0|1) describes

A. all binary strings of length 2

B. all binary strings of length at most 2

C. strings with exactly one 0

D. strings ending in 1""",
    82: """82. Which string is NOT in a∗b∗?

A. aaabbb

B. ab

C. ba

D. ε""",
    83: """83. Which regular expression is most suitable for strings that begin with a and end with b?

A. a∗b∗

B. a(a|b)∗b

C. b(a|b)∗a

D. (a|b)∗""",
    88: """88. If L1 and L2 are regular, then L1 ∪ L2 is

A. regular

B. context-free but not regular

C. non-regular

D. undefined""",
    89: """89. If L1 and L2 are regular, then L1 ∩ L2 is

A. regular

B. always empty

C. never regular

D. only regular when the alphabets differ""",
    90: """90. In a product construction, the transition on symbol a from (p, q) is

A. (δ1(p, a), δ2(q, a))

B. (δ1(p, a), δ1(q, a))

C. (p, q, a)

D. (δ1(p), δ2(q))""",
    93: """93. Machine 1-1 and Machine 1-2 are combined using product construction. The new start state is

A. (q0, q0)

B. (q1, q1)

C. (q2, q2)

D. (q0, q1)""",
    94: """94. When constructing L1 ∪ L2 from two DFAs, the pair state that is final if only the first DFA accepts is

A. final

B. not final

C. undefined

D. the trap state""",
    95: """95. When constructing L1 ∩ L2 from two DFAs, the pair state that is final if only the first DFA accepts is

A. final

B. not final

C. always final

D. the start state""",
    103: """103. Which pair-state criterion corresponds to L1 \\ L2?

A. p final and q nonfinal

B. both final

C. either final

D. both nonfinal""",
    107: """107. In Machine 5-1, the output function value λ(q0) is

A. 0

B. 1

C. a

D. b""",
    108: """108. In Machine 5-1, the output alphabet is

A. {a, b}

B. {0, 1}

C. {q0, q1, q2, q3}

D. {ε}""",
    115: """115. If a Moore machine begins in state q0 with λ(q0) = 1, then before any input is read the output starts with

A. 1

B. 0

C. a

D. nothing at all""",
    116: """116. Which label format is characteristic of a Mealy transition in the diagrams?

A. a;0

B. 0 : a

C. q0 → q1

D. λ(q0) = 1""",
    120: """120. In Machine 5-1, the output associated with state q2 is

A. 0

B. 1

C. a

D. b""",
    121: """121. In Machine 5-2, the output associated with state q3 is

A. 0

B. 1

C. a

D. b""",
    125: """125. A context-free grammar is formally a 4-tuple

A. (Q, Σ, δ, q0)

B. (V, T, S, P)

C. (Q, Γ, F)

D. (L, R, λ)""",
    167: """167. The transition λ, λ; λ from q2 to q3 in Machine 8 represents

A. a nondeterministic guess of the midpoint

B. pushing the first symbol

C. reading the last symbol

D. accepting immediately""",
    168: """168. In Machine 8, the loops on q2 are used to

A. push the first half of the string onto the stack

B. pop the stack

C. empty the tape

D. accept only the empty string""",
    169: """169. In Machine 8, the loops on q3 are used to

A. match and pop symbols from the stack

B. push more input symbols

C. move to the start state

D. create new tape cells""",
    184: """184. In the formal 7-tuple for a TM, (Q, Σ, Γ, δ, q0, b, F), the symbol Γ denotes

A. the tape alphabet

B. the input alphabet

C. the set of final states

D. the transition direction""",
    188: """188. Machine 9 accepts strings of the form

A. 01∗0

B. 10∗1

C. 0∗1∗

D. 1∗01∗""",
    191: """191. In Machine 9, state q1 primarily processes

A. the block of 1s between two 0s

B. the initial blank tape

C. the accept state only

D. the final 0 only""",
    192: """192. In Machine 9, the transition 0;x,R from q0 means

A. read 0, write x, move right

B. read x, write 0, move left

C. write 0, then read x

D. move left without writing""",
}


before_practice, practice_and_after = text.split("## 2. Practice Test Bank (200 Questions)", 1)
practice, after_practice = practice_and_after.split("## 3. Comprehensive Answer Key & Explanations", 1)
for number, replacement in question_repairs.items():
    practice, count = re.subn(
        rf"(?ms)^{number}\. .*?(?=^\d+\. |^### )",
        replacement + "\n\n",
        practice,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"Could not repair question {number}")
text = (
    before_practice
    + "## 2. Practice Test Bank (200 Questions)"
    + practice
    + "## 3. Comprehensive Answer Key & Explanations"
    + after_practice
)

# Source-confirmed notation placement in answer explanations.
answer_repairs = {
    "For B × A,": "For B × A,",
    "one symbol from L1 followed by one from L , so all listed strings belong to the concatenation. 2": "one symbol from L1 followed by one from L2, so all listed strings belong to the concatenation.",
    "Read the first symbol 0 to move to q , then read 1 to move to q . 1 2": "Read the first symbol 0 to move to q1, then read 1 to move to q2.",
    "The first 1 moves to q ; the following 0 returns to q . 1 0": "The first 1 moves to q1; the following 0 returns to q0.",
    "B.Missingtransitionsarecommonlyredirectedtoasink/trapstateincomplete": "B. Missing transitions are commonly redirected to a sink/trap state in complete",
    "The new state set is Q1 × Q2 .": "The new state set is Q1 × Q2.",
    "state label shown for q0 in Machine": "state label shown for q0 in Machine",
    "state label beside q is 0. 2": "state label beside q2 is 0.",
    "state label beside q is 1. 3": "state label beside q3 is 1.",
    "State q2 stores": "State q2 stores",
    "State q compares the second half against the stored prefix. 3": "State q3 compares the second half against the stored prefix.",
    "finally blanks. 01∗0": "finally blanks.",
    "The string 010 fits the pattern.": "The string 010 fits the 01∗0 pattern.",
    "State q loops on 1s, so it handles the middle run of 1s. 1": "State q1 loops on 1s, so it handles the middle run of 1s.",
}
for old, new in answer_repairs.items():
    text = text.replace(old, new)
text = text.replace("context-freegrammarscorrespondto", "context-free grammars correspond to")
text = text.replace("∪L2", "∪ L2").replace("∩L2", "∩ L2")

appendix = """## Appendix Images

### Page 37

![page-37-image-1](final-exam_reviewer_assets/page-37-image-1.png)

![page-37-image-2](final-exam_reviewer_assets/page-37-image-2.png)

![page-37-image-3](final-exam_reviewer_assets/page-37-image-3.png)

### Page 38

![page-38-image-1](final-exam_reviewer_assets/page-38-image-1.png)

![page-38-image-2](final-exam_reviewer_assets/page-38-image-2.png)

![page-38-image-3](final-exam_reviewer_assets/page-38-image-3.png)

### Page 39

![page-39-image-1](final-exam_reviewer_assets/page-39-image-1.png)

![page-39-image-2](final-exam_reviewer_assets/page-39-image-2.png)
"""
text = re.sub(r"(?ms)^## Appendix Images\s*.*\Z", appendix, text)
OUTPUT.write_text(text, encoding="utf-8", newline="\n")
