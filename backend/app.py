from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv
from extract_data import extract_text_from_docx, login_and_get_article

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'docx'

@app.route('/process', methods=['POST'])
def process_request():
    if 'file' not in request.files or 'url' not in request.form:
        return jsonify({"error": "File and URL are required"}), 400

    file = request.files['file']
    target_url = request.form['url']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        docx_text = extract_text_from_docx(file)
    else:
        return jsonify({"error": "Invalid file format. Only .docx files are allowed."}), 400

    try:
        article_text = login_and_get_article(target_url)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    And here is my summary of the article:

    {docx_text}

    Thank you for your help!
    """

    return chat_with_gpt(prompt)

def chat_with_gpt(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150
    )
    return jsonify({"response": response.choices[0].text.strip()})

if __name__ == '__main__':
    app.run(debug=True)
