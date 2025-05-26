import streamlit as st
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string
import PyPDF2
from docx import Document

# Download NLTK data (only needed once)
import nltk
nltk.download('punkt')
nltk.download('stopwords')

# Admin credentials
ADMIN_PASSWORD = "123"

# Session state to store job requirements
if 'job_requirements' not in st.session_state:
    st.session_state.job_requirements = ""

# Initialize stemmer
stemmer = PorterStemmer()

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .stHeader {
        color: #2e86c1;
    }
    .stButton button {
        background-color: #2e86c1;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stTextInput input {
        border-radius: 5px;
        padding: 10px;
    }
    .stTextArea textarea {
        border-radius: 5px;
        padding: 10px;
    }
    .stFileUploader {
        border-radius: 5px;
        padding: 10px;
    }
    .stSuccess {
        color: #28b463;
    }
    .stError {
        color: #e74c3c;
    }
    .stWarning {
        color: #f1c40f;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to preprocess text
def preprocess_text(text):
    # Tokenize
    tokens = word_tokenize(text.lower())
    # Remove punctuation and stopwords
    tokens = [stemmer.stem(word) for word in tokens if word.isalnum() and word not in stopwords.words('english')]
    return set(tokens)

# Function to calculate resume score
def calculate_score(resume_text, job_requirements):
    resume_tokens = preprocess_text(resume_text)
    job_tokens = preprocess_text(job_requirements)
    
    # Calculate matching keywords
    matching_keywords = resume_tokens.intersection(job_tokens)
    # Calculate score as a percentage
    if len(job_tokens) == 0:
        return 0
    score = (len(matching_keywords) / len(job_tokens)) * 100
    return round(score, 2)

# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file):
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Admin Panel
def admin_panel():
    st.header("🔐 Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")
    
    # Only check password if the user has entered something
    if password:
        if password == ADMIN_PASSWORD:
            st.success("✅ Logged in as Admin")
            job_requirements = st.text_area("📝 Enter Job Requirements", st.session_state.job_requirements)
            if st.button("💾 Save Job Requirements"):
                st.session_state.job_requirements = job_requirements
                st.success("🎉 Job Requirements Saved!")
        else:
            st.error("❌ Incorrect Password")

# Client Panel
def client_panel():
    st.header("👤 Client Panel")
    if st.session_state.job_requirements == "":
        st.warning("⚠️ No job requirements set by admin. Please ask the admin to add requirements.")
        return
    
    uploaded_file = st.file_uploader("📂 Upload Your Resume (PDF, DOCX, or TXT file)", type=["pdf", "docx", "txt"])
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        resume_text = ""
        
        try:
            if file_extension == "pdf":
                resume_text = extract_text_from_pdf(uploaded_file)
            elif file_extension == "docx":
                resume_text = extract_text_from_docx(uploaded_file)
            elif file_extension == "txt":
                resume_text = uploaded_file.read().decode("utf-8")
            else:
                st.error("❌ Unsupported file format. Please upload a PDF, DOCX, or TXT file.")
                return
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
            return
        
        st.subheader("📊 Resume Analysis")
        st.write("📄 Your Resume Content:")
        st.text(resume_text)
        
        # Calculate score
        score = calculate_score(resume_text, st.session_state.job_requirements)
        st.subheader(f"🎯 Resume Score: {score}%")
        
        # Display matching keywords
        resume_tokens = preprocess_text(resume_text)
        job_tokens = preprocess_text(st.session_state.job_requirements)
        matching_keywords = resume_tokens.intersection(job_tokens)
        st.write("🔑 Matching Keywords:")
        st.write(matching_keywords)

# Main App
def main():
    st.title("📝 Resume Analyzer")
    st.markdown("---")
    menu = st.sidebar.selectbox("🚀 Select Panel", ["Admin Panel", "Client Panel"])
    
    if menu == "Admin Panel":
        admin_panel()
    elif menu == "Client Panel":
        client_panel()

if __name__ == "__main__":
    main()