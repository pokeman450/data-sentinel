import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_ai_insight(report: dict, filename: str):
    prompt = f"""
You are a senior data engineer reviewing a dataset.

Dataset name: {filename}

Here is the profiling report:
{report}

Your task:
1. Explain what is wrong in simple terms
2. Identify key data quality risks
3. Suggest concrete fixes
4. Keep response concise and structured

Return in bullet points.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a senior data engineering assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content