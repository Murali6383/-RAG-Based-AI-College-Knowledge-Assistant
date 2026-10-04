from app.config import GROQ_API_KEY, GROQ_MODEL
from groq import Groq


print("API key loaded:", bool(GROQ_API_KEY))
print("Model:", GROQ_MODEL)


client = Groq(
    api_key=GROQ_API_KEY
)


response = client.chat.completions.create(

    model=GROQ_MODEL,

    messages=[
        {
            "role": "system",
            "content": (
                "Answer only using the supplied text."
            )
        },
        {
            "role": "user",
            "content": """
Evidence:
The minimum attendance required
to write the end-semester examination
is 75%.

Question:
What is the minimum attendance?
"""
        }
    ],

    temperature=0.0,

    max_completion_tokens=300
)


print("\n========== GROQ TEST ==========")

print(
    response.choices[0].message.content
)