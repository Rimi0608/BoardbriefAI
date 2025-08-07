import os
import fitz  # PyMuPDF
import pandas as pd
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def parse_documents(file_paths: list, prompt: str) -> str:
    raw_contents = []
    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.pdf':
            try:
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                raw_contents.append(text)
            except Exception as e:
                continue

        elif ext == '.csv':
            try:
                df = pd.read_csv(file_path)
                markdown = df.to_markdown(index=False)
                raw_contents.append(markdown)
            except Exception:
                continue

        elif ext in ['.xls', '.xlsx']:
            try:
                df = pd.read_excel(file_path)
                markdown = df.to_markdown(index=False)
                raw_contents.append(markdown)
            except Exception:
                continue

        else:
            continue

    raw_content = "\n\n".join(raw_contents)

    final_prompt = (
        f"You are a business analyst. Please read the following document content and provide a clean, "
        f"well-structured summary of its key information, data points, and primary topics. "
        f"Here is the user's specific request: '{prompt}'. "
        f"Content: `{raw_content}`"
    )

    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(final_prompt)

    structured_summary = response.text.strip()
    return structured_summary
