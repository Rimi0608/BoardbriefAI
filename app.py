import os
import shutil
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS

from parser import parse_documents
from insights import generate_insights
from ppt_generator import create_presentation

UPLOAD_FOLDER = "uploaded_files"
ALLOWED_EXTENSIONS = {".pdf", ".csv", ".xls", ".xlsx"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Max 50MB upload


def allowed_file(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    if 'files' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400

    files = request.files.getlist("files")
    prompt = request.form.get('prompt', '') # Get the prompt from the form data

    if not files or len(files) == 0 or files[0].filename == '':
        return jsonify({"error": "No files uploaded"}), 400

    saved_file_paths = []
    try:
        for file in files:
            filename = secure_filename(file.filename)
            if filename == "":
                continue
            
            if not allowed_file(filename):
                return jsonify({"error": f"File type not allowed: {filename}"}), 400

            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            saved_file_paths.append(save_path)

        if not saved_file_paths:
            return jsonify({"error": "No valid files were uploaded"}), 400

        structured_summary = parse_documents(saved_file_paths, prompt)
        if not structured_summary:
            return jsonify({"error": "Failed to parse document contents"}), 500

        insights_data = generate_insights(structured_summary)
        presentation_data = create_presentation(structured_summary)

        final_response = {
            "summary": presentation_data.get("summary", ""),
            "highlights": presentation_data.get("highlights", []),
            "slides": presentation_data.get("slides", []),
            "insights": insights_data,
            "download_link": "/api/download/presentation"
        }

        return jsonify(final_response), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    finally:
        for path in saved_file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                print(f"Error cleaning up file {path}: {e}")

@app.route("/api/download/presentation")
def download_presentation():
    # In a real app, you would generate the presentation file here
    # For this example, we'll just send back a dummy file
    presentation_path = "sample_presentation.pptx"
    if not os.path.exists(presentation_path):
        # Create a dummy file if it doesn't exist
        with open(presentation_path, "w") as f:
            f.write("This is a dummy presentation.")
            
    return send_file(presentation_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
