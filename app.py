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

uploaded_pdf = st.file_uploader("Upload a Resume PDF", type="pdf")



# --- Initialize session state ---
if 'resume_json' not in st.session_state:
    st.session_state.resume_json = None
if 'optimized_json' not in st.session_state:
    st.session_state.optimized_json = None

# --- Step 1: Upload PDF ---
if uploaded_pdf and openai_key:
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "resume.pdf")
        with open(pdf_path, "wb") as f:
            f.write(uploaded_pdf.read())

        st.success("PDF uploaded successfully.")

        try:
            with st.spinner("Reading PDF..."):
                # Here we assume convert_pdf_to_json directly returns a dictionary
                resume_json = convert_pdf_to_json(pdf_path, openai_key)
                st.session_state.resume_json = resume_json

                # Save for later
                with open("resume.json", "w") as f:
                    json.dump(resume_json, f, indent=2)

            st.success("Resume converted successfully.")

        except Exception as e:
            st.error(f"Error converting PDF: {e}")

# --- Step 2: Enter Job Description ---
if st.session_state.resume_json:
    job_description = st.text_area("Enter the Job Description", placeholder="Looking for a data scientist with experience in Python, SQL, machine learning...")

    if job_description.strip():
        if st.button("Optimize Resume"):
            progress_bar = st.progress(0)
            try:
                progress_bar.progress(10)

                related_templates = get_related_template(chroma_db, job_description)
                progress_bar.progress(30)

                optimized_json = optimize_resume("resume-prompt.json", related_templates, job_description)
                st.session_state.optimized_json = optimized_json

                with open("optimized_resume.json", "w") as f:
                    json.dump(optimized_json, f, indent=2)

                progress_bar.progress(60)

                # Update resume
                base_dir = os.path.dirname(__file__)
                prompt_path = os.path.join(base_dir, "optimized_resume.json")
                resume_path = os.path.join(base_dir, "resume.json")

                updated_json = update_relevant_json(prompt_path, resume_path)

                with open("updated_resume.json", "w") as f:
                    json.dump(updated_json, f, indent=2)

                progress_bar.progress(80)

                # Convert to final PDF
                final_pdf_path = convert_json_to_pdf(updated_json)

                progress_bar.progress(100)
                st.success("Resume optimized successfully.")

                with open(final_pdf_path, "rb") as f:
                    st.download_button(
                        label="Download Optimized Resume (PDF)",
                        data=f,
                        file_name="optimized_resume.pdf",
                        mime="application/pdf"
                    )

            except Exception as e:
                st.error(f"Error optimizing resume: {e}")
                progress_bar.empty()



# if uploaded_pdf and openai_key:
#     with tempfile.TemporaryDirectory() as tmpdir:
#         # Save uploaded PDF
#         pdf_path = os.path.join(tmpdir, "resume.pdf")
#         with open(pdf_path, "wb") as f:
#             f.write(uploaded_pdf.read())

#         st.success("PDF uploaded successfully.")
        
#         job_description= st.text_area("Enter Job Description", "Need a data scientist with experience in Python, SQL, and machine learning.")
#         related_templates = get_related_template(chroma_db,job_description)


#         try:
#             st.info("Converting PDF to JSON...")
#             resume_json = convert_pdf_to_json(pdf_path, openai_key)
#             # Save JSON to file
#             with open("resume.json", "w") as f:
#                 json.dump(resume_json, f, indent=2)
#             st.success("Converted PDF to JSON.")
#             extract_relevant_json(resume_json) 
#             optimized_json=optimize_resume("resume-prompt.json", related_templates, job_description)
#             with open("optimized_resume.json", "w") as f:
#                 json.dump(optimized_json, f, indent=2)  

#             st.success("Finetuned resume.")
        
#             base_dir = os.path.dirname(__file__)  # directory where your .py file is
#             prompt_path = os.path.join(base_dir, "optimized_resume.json")
#             resume_path = os.path.join(base_dir, "resume.json")
#             st.write(os.getcwd())  # See where Streamlit thinks the current folder is
#             st.write(os.path.exists("optimized_resume.json"))
#             st.write(os.path.exists("resume.json"))

#             updated_json=update_relevant_json(prompt_path,resume_path)
#             with open("updated_resume.json", "w") as f:
#                 json.dump(updated_json, f, indent=2) 
#             json_str = json.dumps(updated_json, indent=2)
#             st.success("Updated resume JSON.")
#             # Convert back to PDF
#             pdf_path = convert_json_to_pdf(updated_json)
#             with open(pdf_path, "rb") as f:
#                 st.download_button("Download PDF", f, "updated_resume.pdf", "application/pdf")

#         except Exception as e:
#             st.error(f"Something went wrong: {e}")

# if uploaded_pdf and openai_key:
#     with tempfile.TemporaryDirectory() as tmpdir:
#         # Save uploaded PDF
#         pdf_path = os.path.join(tmpdir, "resume.pdf")
#         with open(pdf_path, "wb") as f:
#             f.write(uploaded_pdf.read())

#         st.success("PDF uploaded successfully.")
        
#         job_description= st.text_area("Enter Job Description", "Need a data scientist with experience in Python, SQL, and machine learning.")
#         related_templates = get_related_template(chroma_db,job_description)


#         try:
#             st.info("Converting PDF to JSON...")
#             resume_json = convert_pdf_to_json(pdf_path, openai_key)
#             # Save JSON to file
#             with open("resume.json", "w") as f:
#                 json.dump(resume_json, f, indent=2)
#             st.success("Converted PDF to JSON.")
#             extract_relevant_json(resume_json) 
#             optimized_json=optimize_resume("resume-prompt.json", related_templates, job_description)
#             with open("optimized_resume.json", "w") as f:
#                 json.dump(optimized_json, f, indent=2)  

#             st.success("Finetuned resume.")
        
#             base_dir = os.path.dirname(__file__)  # directory where your .py file is
#             prompt_path = os.path.join(base_dir, "optimized_resume.json")
#             resume_path = os.path.join(base_dir, "resume.json")
#             st.write(os.getcwd())  # See where Streamlit thinks the current folder is
#             st.write(os.path.exists("optimized_resume.json"))
#             st.write(os.path.exists("resume.json"))

#             updated_json=update_relevant_json(prompt_path,resume_path)
#             with open("updated_resume.json", "w") as f:
#                 json.dump(updated_json, f, indent=2) 
#             json_str = json.dumps(updated_json, indent=2)
#             st.success("Updated resume JSON.")
#             # Convert back to PDF
#             pdf_path = convert_json_to_pdf(updated_json)
#             with open(pdf_path, "rb") as f:
#                 st.download_button("Download PDF", f, "updated_resume.pdf", "application/pdf")

#         except Exception as e:
#             st.error(f"Something went wrong: {e}")
