import streamlit as st
from PyPDF2 import PdfReader
from google import genai
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus
import re

load_dotenv()

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

st.title("📄 AI Resume Analyzer")
st.write("Upload your resume and get an AI-powered analysis.")

uploaded_file = st.file_uploader("Choose your Resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    st.subheader("📄 Resume")
    st.write(text)
    st.divider()

    if st.button("🚀 Analyze Resume"):
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        prompt = f"""
You are an expert AI Resume Analyzer.

Analyze the following resume.

{text}

Return ONLY plain text.

Do NOT return HTML.
Do NOT return CSS.
Do NOT return XML.
Do NOT return Markdown code blocks.
Do NOT use <div>, <span>, <style>, or any HTML tags.

Provide the following sections exactly:

Resume Score: XX/100
ATS Score: XX/100

Main Skills:
- Skill 1
- Skill 2

Strengths:
- Point 1
- Point 2

Missing Skills:
- Point 1
- Point 2

JOB ROLES:
1. Job Role
2. Job Role
3. Job Role
4. Job Role
5. Job Role

Suggestions:
- Suggestion 1
- Suggestion 2
"""

        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )
        except Exception as e:
            error = str(e)
            if "429" in error or "RESOURCE_EXHAUSTED" in error:
                st.error("⚠️ Gemini API quota exceeded. Please try again later.")
                st.stop()
            st.error(error)
            st.stop()

        clean_response = re.sub(r"<[^>]+>", "", response.text)

        st.subheader("🤖 AI Resume Analysis")

        st.markdown("""
<style>
.score-card{
background-color:#f8f9fa;
border:1px solid #dddddd;
border-radius:15px;
padding:20px;
text-align:center;
margin-bottom:20px;
}
.score-title{font-size:22px;font-weight:bold;}
.score-number{font-size:42px;font-weight:bold;color:#2E86C1;}
</style>
""", unsafe_allow_html=True)

        resume_match = re.search(r"Resume Score\s*:\s*(\d+)\s*/\s*100", clean_response, re.IGNORECASE)
        ats_match = re.search(r"ATS Score\s*:\s*(\d+)\s*/\s*100", clean_response, re.IGNORECASE)

        resume_score = int(resume_match.group(1)) if resume_match else 0
        ats_score = int(ats_match.group(1)) if ats_match else 0

        status = "⚠️ Needs Improvement"
        if resume_score >= 80:
            status = "🌟 Excellent Resume"
        elif resume_score >= 60:
            status = "✅ Good Resume"

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
<div class="score-card">
<div class="score-title">Resume Score</div>
<div class="score-number">{resume_score}/100</div>
<div>{status}</div>
</div>
""", unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
<div class="score-card">
<div class="score-title">ATS Score</div>
<div class="score-number">{ats_score}/100</div>
</div>
""", unsafe_allow_html=True)

        st.write(clean_response)

        st.subheader("💼 Recommended Jobs")

        job_roles = re.findall(r"^\d+\.\s*(.+)$", clean_response, re.MULTILINE)

        if not job_roles:
            st.warning("No job roles found.")
        else:
            for role in job_roles:
                query = quote_plus(role)
                st.markdown(f"### 💼 {role}")
                st.markdown(f"🔗 [LinkedIn Jobs](https://www.linkedin.com/jobs/search/?keywords={query})")
                st.markdown(f"🔗 [Naukri Jobs](https://www.naukri.com/{query}-jobs)")
                st.markdown(f"🔗 [Indeed Jobs](https://in.indeed.com/jobs?q={query})")
                st.divider()