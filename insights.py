import os
import json
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def generate_insights(structured_text: str) -> dict:
    prompt = (
        f"Analyze the following business summary. Identify the top 3-5 key categories or segments "
        f"and estimate their numerical distribution (e.g., sales, budget, market share). Return ONLY a valid JSON object with the following structure: "
        f'{{ "labels": ["Category 1", "Category 2", ...], "data": [value1, value2, ...] }}. '
        f"Do not include any other text or markdown formatting. Summary: `{structured_text}`"
    )

    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)

    try:
        content = response.text.strip().replace("```json", "").replace("```", "").strip()
        parsed_json = json.loads(content)
    except (json.JSONDecodeError, AttributeError):
        return {
            "labels": [],
            "datasets": [{
                "data": [],
                "backgroundColor": []
            }]
        }

    base_colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
    data_len = len(parsed_json.get("data", []))
    background_colors = base_colors[:data_len]

    result = {
        "labels": parsed_json.get("labels", []),
        "datasets": [{
            "data": parsed_json.get("data", []),
            "backgroundColor": background_colors,
        }]
    }

    return result
