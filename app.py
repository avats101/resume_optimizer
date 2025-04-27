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
job_description = st.text_area("Enter Job Description", "Need a data scientist with experience in Python, SQL, and machine learning.", height=300)

optimize_button = st.button("Optimize Resume")

if optimize_button:

    if uploaded_pdf and openai_key and job_description:
        
        st.write(f"Job Description: {job_description}")
        # Progress bar setup
        progress = st.progress(0)
        progress_text = st.empty()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                # Step 1: Save PDF
                pdf_path = os.path.join(tmpdir, "resume.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(uploaded_pdf.read())
                progress.progress(0.1)  # Update progress
                progress_text.text("PDF uploaded successfully...")

                # Step 2: Read and convert PDF to JSON
                st.info("Reading PDF..")
                resume_json = convert_pdf_to_json(pdf_path, openai_key)
                with open("resume.json", "w") as f:
                    json.dump(resume_json, f, indent=2)
                progress.progress(0.3)  # Update progress
                progress_text.text("Converted PDF to JSON...")

                # Step 3: Extract relevant JSON
                extract_relevant_json(resume_json)
                progress.progress(0.4)  # Update progress
                progress_text.text("Extracted relevant information from resume...")

                # Step 4: Optimize Resume
                related_templates = get_related_template(chroma_db, job_description)
                optimized_json = optimize_resume("resume-prompt.json", related_templates, job_description)
                with open("optimized_resume.json", "w") as f:
                    json.dump(optimized_json, f, indent=2)
                progress.progress(0.6)  # Update progress
                progress_text.text("Optimized resume...")

                # Step 5: Update Resume JSON
                base_dir = os.path.dirname(__file__)
                prompt_path = os.path.join(base_dir, "optimized_resume.json")
                resume_path = os.path.join(base_dir, "resume.json")
                updated_json = update_relevant_json(prompt_path, resume_path)
                with open("updated_resume.json", "w") as f:
                    json.dump(updated_json, f, indent=2)
                progress.progress(0.8)  # Update progress
                progress_text.text("Updated resume JSON...")

                # Step 6: Convert back to PDF
                st.success("Generating PDF...")
                pdf_path = convert_json_to_pdf(updated_json)
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF", f, "updated_resume.pdf", "application/pdf")
                progress.progress(1.0)  # Complete progress
                progress_text.text("Resume optimization completed. Download your updated resume.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                progress.progress(0.0)  # Reset progress if something fails
                progress_text.text("An error occurred. Please try again.")
    else:
        st.error("Please upload all required inputs (PDF, API key, and Job Description).")

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/resume.png", width=80)
    st.markdown("## Guide & Tips")
    
    with st.expander("About ATS Systems", expanded=False):
        st.markdown("""
        **Applicant Tracking Systems (ATS)** scan your resume before a human ever sees it.
        
        Key points:
        - 75% of resumes are rejected by ATS before reaching a recruiter
        - Simple formatting increases your chances
        - Keyword matching is crucial for passing ATS filters
        """)
    
    with st.expander("Resume Best Practices", expanded=False):
        st.markdown("""
        1. **Be Specific**: Use numbers and metrics to quantify achievements
        2. **Customize**: Tailor your resume for each job application
        3. **Format Properly**: Use consistent headers and bullet points
        4. **Focus on Relevance**: Prioritize relevant experience
        5. **Check for Typos**: Spelling and grammar errors create poor impressions
        """)
    
    with st.expander("Keyword Optimization Tips", expanded=True):
        st.markdown("""
        ✅ Include technical skills mentioned in the job description
        
        ✅ Match the exact phrasing used in the listing
        
        ✅ Include both acronyms and spelled-out versions (e.g., "UI/UX" and "User Interface")
        
        ✅ Use industry-standard terminology
        
        ✅ Include soft skills that match the company culture
        """)
    
    st.markdown("---")
    st.markdown("### Need help?")
    help_option = st.selectbox(
        "Choose an option:",
        ["Select", "Common Resume Mistakes", "What to Include", "ATS Compatibility Issues"]
    )
    
    if help_option == "Common Resume Mistakes":
        st.info("""
        - **Too generic**: Not tailoring to specific job
        - **Wall of text**: Poor formatting and readability
        - **Missing keywords**: Not including terms from job description
        - **Too long**: Exceeding 2 pages for most roles
        - **Focusing on duties**: Not highlighting accomplishments
        """)
    elif help_option == "What to Include":
        st.info("""
        - **Professional summary**: 2-3 sentences highlighting your value
        - **Relevant skills**: Both technical and soft skills
        - **Work experience**: Focus on achievements, not just responsibilities
        - **Education**: Degrees, certifications, relevant coursework
        - **Projects**: Highlight relevant work with measurable outcomes
        """)
    elif help_option == "ATS Compatibility Issues":
        st.info("""
        - **Complex formatting**: Tables, headers, footers, columns
        - **Images & graphics**: Most ATS can't read these
        - **Non-standard section headings**: Stick to conventional titles
        - **PDF compatibility**: Ensure PDFs are text-based, not scanned
        - **File naming**: Use simple names (FirstName_LastName_Resume.pdf)
        """)
