import os
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, AuthenticationError, OpenAIError

load_dotenv()


def get_client():
    """
    Returns OpenAI client if API key exists, otherwise None.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    return OpenAI(api_key=api_key)


def generate_ai_insight(report: dict, filename: str):
    """
    AI analysis with safe fallback for missing key, quota issues, or API errors.
    """

    client = get_client()

    if client is None:
        return "AI disabled: OPENAI_API_KEY not configured."

    # Prevent huge payloads from breaking or costing too much
    if len(str(report)) > 15000:
        return "AI disabled: report too large for analysis."

    prompt = f"""
You are a senior data engineer.

Dataset: {filename}

Report:
{report}

Provide insights:
- issues
- risks
- recommendations
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a senior data engineer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except RateLimitError:
        return "AI disabled: quota exceeded (rate limit / billing issue)."

    except AuthenticationError:
        return "AI disabled: invalid API key."

    except OpenAIError as e:
        return f"AI disabled: OpenAI API error - {str(e)}"

    except Exception as e:
        return f"AI error (unexpected): {str(e)}"