from flask import Flask, render_template, request, jsonify
import chromadb
import os
import time
import git
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Config
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"py", "txt"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ChromaDB setup
chroma_client = chromadb.PersistentClient(path="./memory.db")
collection = chroma_client.get_or_create_collection("coding_memory")

# Git setup
REPO_DIR = os.path.abspath("project_repo")
if not os.path.exists(REPO_DIR):
    os.makedirs(REPO_DIR)
    repo = git.Repo.init(REPO_DIR)
    repo.create_remote("origin", "https://github.com/sandahltim/ai-coder-local.git")
else:
    repo = git.Repo(REPO_DIR)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]
    past_context = collection.query(query_texts=[user_input], n_results=3)
    context_str = "\n".join(past_context["documents"][0]) if past_context["documents"] else "No prior context."
    prompt = f"Previous context:\n{context_str}\n\nUser query: {user_input}\nAnswer as a coding assistant."
    # Placeholder response until CodeLLaMA is added
    ai_response = "Local AI response coming soon after CUDA setup!"

    collection.add(
        documents=[f"Input: {user_input}\nResponse: {ai_response}"],
        metadatas=[{"timestamp": str(time.time())}],
        ids=[str(os.urandom(16).hex())]
    )
    return jsonify({"response": ai_response})

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        with open(filepath, "r") as f:
            file_content = f.read()

        prompt = f"Analyze or modify this code:\n\n{file_content}\n\nProvide your response as a coding assistant."
        # Placeholder response
        ai_response = f"Local AI will process {filename} soon!"

        collection.add(
            documents=[f"Uploaded file: {filename}\nContent: {file_content}\nResponse: {ai_response}"],
            metadatas=[{"timestamp": str(time.time())}],
            ids=[str(os.urandom(16).hex())]
        )

        repo_path = os.path.join(REPO_DIR, filename)
        os.makedirs(os.path.dirname(repo_path), exist_ok=True)
        with open(repo_path, "w") as f:
            f.write(file_content)
        repo.index.add([repo_path])
        repo.index.commit(f"Uploaded {filename}")
        try:
            repo.git.pull("origin", "main")
            repo.git.push("origin", "main")
        except git.GitCommandError as e:
            return jsonify({"error": f"Git error: {str(e)}"}), 500

        return jsonify({"response": ai_response, "filename": filename})
    return jsonify({"error": "File type not allowed"}), 400

@app.route("/git_status", methods=["GET"])
def git_status():
    status = repo.git.status()
    return jsonify({"status": status})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)  # Port 5001 to avoid conflict