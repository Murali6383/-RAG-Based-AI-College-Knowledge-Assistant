from app.grounding import check_grounding


# --------------------------------------------------
# TEST 1: Attendance question
# --------------------------------------------------

question = "I have 70% attendance. Can I attend the exam?"

evidence = """
Students must have a minimum of 75% attendance
to be eligible to write the examination.
"""

result = check_grounding(question, evidence)

print("TEST 1 - ATTENDANCE")
print(result)


# --------------------------------------------------
# TEST 2: Google question
# --------------------------------------------------

question = "What CGPA does Google require for placement?"

evidence = """
Minimum CGPA of 6.5 is required for campus placement.
Companies may set higher cut-offs.
"""

result = check_grounding(question, evidence)

print("\nTEST 2 - GOOGLE")
print(result)


# --------------------------------------------------
# TEST 3: General placement question
# --------------------------------------------------

question = "What is the minimum CGPA required for placement?"

evidence = """
Minimum CGPA of 6.5 is required for campus placement.
Companies may set higher cut-offs.
"""

result = check_grounding(question, evidence)

print("\nTEST 3 - PLACEMENT")
print(result)