import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3
import streamlit as st
import os
import tempfile
import json

from convert_pdf_to_json import convert_pdf_to_json
from convert_json_to_pdf import convert_json_to_pdf
from template_retrival import set_chroma_db, get_related_template
from finetune import optimize_resume
from parse_resume import extract_relevant_json, update_relevant_json
from data.resume_templates import RESUME_TEMPLATES


st.title("Resume Optimizer")
chroma_db=set_chroma_db(RESUME_TEMPLATES)

openai_key = st.text_input("Enter your OpenAI API Key", type="password")
uploaded_pdf = st.file_uploader("Upload your Resume", type="pdf")
job_description= st.text_area("Enter Job Description", "Need a data scientist with experience in Python, SQL, and machine learning.")
if job_description:
    related_templates = get_related_template(chroma_db,job_description)
if uploaded_pdf and openai_key and job_description:
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save uploaded PDF
        pdf_path = os.path.join(tmpdir, "resume.pdf")
        with open(pdf_path, "wb") as f:
            f.write(uploaded_pdf.read())
        st.success("PDF uploaded successfully.")
        try:
            st.info("Reading PDF..")
            resume_json = convert_pdf_to_json(pdf_path, openai_key)
            # Save JSON to file
            with open("resume.json", "w") as f:
                json.dump(resume_json, f, indent=2)
            st.success("Converted PDF to JSON..")
            extract_relevant_json(resume_json) 
            optimized_json=optimize_resume("resume-prompt.json", related_templates, job_description)
            with open("optimized_resume.json", "w") as f:
                json.dump(optimized_json, f, indent=2)  

            st.success("Resume is optimized.")
        
            base_dir = os.path.dirname(__file__)  # directory where your .py file is
            prompt_path = os.path.join(base_dir, "optimized_resume.json")
            resume_path = os.path.join(base_dir, "resume.json")
            st.write(os.getcwd())  # See where Streamlit thinks the current folder is
            st.write(os.path.exists("optimized_resume.json"))
            st.write(os.path.exists("resume.json"))
            st.success("Updating Resume JSON.")
            updated_json=update_relevant_json(prompt_path,resume_path)
            with open("updated_resume.json", "w") as f:
                json.dump(updated_json, f, indent=2) 
            json_str = json.dumps(updated_json, indent=2)
            st.success("Generating PDF.")
            # Convert back to PDF
            pdf_path = convert_json_to_pdf(updated_json)
            with open(pdf_path, "rb") as f:
                st.download_button("Download PDF", f, "updated_resume.pdf", "application/pdf")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
