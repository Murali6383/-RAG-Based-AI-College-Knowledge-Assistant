from app.rule_engine import check_policy_rule


# ============================================================
# TEST 1 - ATTENDANCE
# ============================================================

question = "I have 70% attendance. Can I write the exam?"

evidence = """
Students must have a minimum of 75% attendance
to be eligible to write the examination.
"""

print("\nTEST 1 - ATTENDANCE")

result = check_policy_rule(
    question,
    evidence
)

print(result)


# ============================================================
# TEST 2 - CGPA
# ============================================================

question = "My CGPA is 6.2. Can I attend campus placement?"

evidence = """
Minimum CGPA of 6.5 is required for campus placement.
Companies may set higher cut-offs.
"""

print("\nTEST 2 - CGPA")

result = check_policy_rule(
    question,
    evidence
)

print(result)


# ============================================================
# TEST 3 - CGPA ELIGIBLE
# ============================================================

question = "My CGPA is 7.2. Can I attend campus placement?"

evidence = """
Minimum CGPA of 6.5 is required for campus placement.
Companies may set higher cut-offs.
"""

print("\nTEST 3 - CGPA ELIGIBLE")

result = check_policy_rule(
    question,
    evidence
)

print(result)


# ============================================================
# TEST 4 - ARREARS
# ============================================================

question = "I have 2 arrears. Can I attend campus placement?"

evidence = """
Students must have no standing arrears
at the time of the placement drive.
"""

print("\nTEST 4 - ARREARS")

result = check_policy_rule(
    question,
    evidence
)

print(result)