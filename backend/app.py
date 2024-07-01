from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv
import docx2txt

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'docx'

def extract_text_from_docx(file):
    return docx2txt.process(file)

@app.route('/process', methods=['POST'])
def process_request():
    if 'article_file' not in request.files or 'writing_file' not in request.files:
        return jsonify({"error": "Article file and writing file are required"}), 400

    article_file = request.files['article_file']
    writing_file = request.files['writing_file']

    if article_file.filename == '' or writing_file.filename == '':
        return jsonify({"error": "No selected file(s)"}), 400

    if not (allowed_file(article_file.filename) and allowed_file(writing_file.filename)):
        return jsonify({"error": "Invalid file format. Only .docx files are allowed."}), 400

    article_text = extract_text_from_docx(article_file)
    writing_text = extract_text_from_docx(writing_file)

    prompt = f"""
    Hello, ChatGPT! I am working on improving my academic writing skills, and I would like your assistance in practicing summarizing scholarly articles. I will provide you with a scholarly article, and my task will be to write a concise and accurate summary of it.

    Here is how I would like you to assist me:

    1. **Summary Feedback**:
        - Please read the summary I have written and provide me with detailed feedback. Focus on the following aspects:
            - **Clarity**: Is the summary clear and easy to understand?
            - **Accuracy**: Does the summary accurately reflect the main points and arguments of the article?
            - **Conciseness**: Is the summary concise without omitting important information?
            - **Structure**: Is the summary well-organized and logically structured?
            - **Language**: Is the language appropriate for an academic summary? Are there any grammatical errors or awkward phrasing that need to be corrected?

    2. **Suggestions for Improvement**:
        - Provide specific suggestions on how I can improve the summary. This could include rephrasing sentences, adding or removing content, or reorganizing the structure.

    3. **Strengths and Weaknesses**:
        - Highlight the strengths of my summary to let me know what I am doing well.
        - Identify the weaknesses or areas where I need more practice or improvement.

    4. **Examples**:
        - If possible, provide examples of how a particular section or sentence can be improved or rewritten for better clarity and impact.

    Here is the article for this exercise: {article_text}
    And here is my summary of the article:{writing_text}

    Note: Please do not use any external data or knowledge apart from the information provided in this prompt.

    Thank you for your help!
    """

    return chat_with_gpt(prompt)

def chat_with_gpt(prompt):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-0125",
        prompt=prompt
    )
    return jsonify({"response": response.choices[0].text.strip()})

if __name__ == '__main__':
    app.run(debug=True)
