import os
import glob
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from docx import Document
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq

app = Flask(__name__, static_url_path='/static')

# API Key (Use environment variable for security)
API_KEY = os.getenv("GROQ_API_KEY", "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")

# Define directory containing .docx files
docx_directory = "./data"

# Initialize the QA chain
qa_chain = None

# System message defining the AI's behavior
SYSTEM_MESSAGE = (
    "Your name is Zhaim. "
    "You are a friendly and intelligent AI assistant designed for general conversation and providing useful information. You can engage in casual discussions, answer general knowledge questions, and help with a wide range of topics. "
    "You must only use information from the provided documents when the user explicitly asks about them. Never volunteer details about the user or the documents unless directly requested. "
    "If the user asks a general question, respond normally without referencing any private or stored details. If they ask about a topic that requires document retrieval, fetch the relevant details and present them concisely. "
    "Maintain a warm and engaging tone, but respect the user's privacy at all times. If the user asks an unclear or broad question, seek clarification before proceeding."
)

def initialize_qa_system():
    global qa_chain
    
    # Function to load and extract text from .docx files
    def load_docx_files(directory):
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Error: The directory '{directory}' does not exist.")
        
        text_data = ""
        docx_files = glob.glob(os.path.join(directory, "*.docx"))

        if not docx_files:
            raise FileNotFoundError("Error: No .docx files found in the directory.")

        for file_path in docx_files:
            doc = Document(file_path)
            for para in doc.paragraphs:
                text_data += para.text + "\n"
        
        return text_data

    try:
        # Extract text from docx files
        docx_text = load_docx_files(docx_directory)

        # Split text into smaller chunks for vector storage
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_text(docx_text)

        # Create vector database using HuggingFace embeddings
        embeddings = HuggingFaceEmbeddings()
        db = FAISS.from_texts(texts, embeddings)
        retriever = db.as_retriever()

        # Initialize ChatGroq LLM
        llm = ChatGroq(
            api_key=API_KEY,
            model_name="llama3-70b-8192"
        )

        # Create retrieval-based QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm, 
            retriever=retriever
        )
        
        return True
    except Exception as e:
        print(f"Error initializing QA system: {e}")
        return False

# Routes for static files (CSS, JS)
@app.route('/static/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('static/css', filename)

@app.route('/static/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('static/js', filename)

# Route for the home page
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/home.html')
def home():
    return render_template('home.html')

@app.route('/llm.html')
def llm():
    return render_template('llm.html')

# API endpoint for LLM queries
@app.route('/query', methods=['POST'])
def process_query():
    global qa_chain
    
    if not qa_chain:
        success = initialize_qa_system()
        if not success:
            return jsonify({"error": "Failed to initialize the QA system. Please check logs."})
    
    data = request.json
    user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({"error": "Empty query"})
    
    try:
        # Include system message in the query
        formatted_query = f"{SYSTEM_MESSAGE}\n\nUser Query: {user_query}"
        
        response = qa_chain.invoke(formatted_query)
        return jsonify({"response": response["result"]})
    except Exception as e:
        return jsonify({"error": f"Error processing query: {str(e)}"})

if __name__ == "__main__":
    # Initialize the QA system when the app starts
    initialize_qa_system()
    
    # Run the Flask app
    app.run(debug=True)