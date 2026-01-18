import streamlit as st
from PyPDF2 import PdfReader
import re

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Resume Analyzer",
    layout="centered",
    page_icon="📄"
)

st.markdown("<h1 style='text-align: center;'>📄 Resume Analyzer</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center;'>Analyze your Resume vs Job Description and identify skill gaps</p>",
    unsafe_allow_html=True
)

st.divider()

# -----------------------------
# Skill Keywords (NOT a DB)
# -----------------------------
SKILLS_DB = [
    "python", "java", "c++", "sql", "mysql", "mongodb",
    "html", "css", "javascript", "react", "angular",
    "nodejs", "express", "django", "flask",
    "machine learning", "deep learning", "data science",
    "pandas", "numpy", "matplotlib",
    "power bi", "tableau",
    "aws", "azure", "docker", "git", "linux",
    "testing", "debugging", "sdlc",
    "software development", "software engineering",
    "api", "rest"
]

# -----------------------------
# Helper Functions
# -----------------------------
def extract_text_from_pdf(file):
    text = ""
    reader = PdfReader(file)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "
    return text.lower()


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def extract_skills(text):
    """
    Extract only meaningful skill keywords using word-boundary matching
    """
    text = clean_text(text)
    found_skills = set()

    for skill in SKILLS_DB:
        # 🚫 Ignore dangerous single-letter skills like "c"
        if skill == "c":
            continue

        words = skill.split()
        pattern = r"\b" + r"\s+".join(map(re.escape, words)) + r"\b"

        if re.search(pattern, text):
            found_skills.add(skill)

    return found_skills


def resume_suggestions(missing_skills):
    if missing_skills:
        return [
            "Add projects that demonstrate the missing skills.",
            "Include certifications or online courses related to the missing skills.",
            "Highlight hands-on experience in your resume.",
            "Customize your resume keywords based on the job description."
        ]
    else:
        return ["Your resume matches the job description very well."]

# -----------------------------
# Inputs Section
# -----------------------------
st.subheader("📥 Upload Inputs")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

jd_input_type = st.radio(
    "Job Description Input Type",
    ["Upload PDF", "Paste Text"]
)

jd_text = ""

if jd_input_type == "Upload PDF":
    jd_file = st.file_uploader("Upload Job Description (PDF)", type=["pdf"])
    if jd_file:
        jd_text = extract_text_from_pdf(jd_file)

else:
    jd_text = st.text_area(
        "Paste Job Description Here",
        height=200,
        placeholder="Paste the full job description here..."
    )

st.divider()

# -----------------------------
# Analyze Button
# -----------------------------
if st.button("🔍 Analyze Resume", use_container_width=True):

    if not resume_file:
        st.error("Please upload your resume.")
        st.stop()

    if not jd_text.strip():
        st.error("Please provide a job description (PDF or text).")
        st.stop()

    with st.spinner("Analyzing resume and job description..."):
        resume_text = extract_text_from_pdf(resume_file)

        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)

        # JD is source of truth
        matched_skills = sorted(jd_skills & resume_skills)
        missing_skills = sorted(jd_skills - resume_skills)

        match_percentage = (
            int(len(matched_skills) / len(jd_skills) * 100)
            if jd_skills else 0
        )

    # -----------------------------
    # Results
    # -----------------------------
    st.subheader("📊 Analysis Results")

    st.metric("Skill Match Percentage", f"{match_percentage}%")
    st.progress(match_percentage / 100 if match_percentage else 0)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ Resume Skills")
        st.success(", ".join(sorted(resume_skills)) if resume_skills else "No skills detected")

    with col2:
        st.markdown("### 📌 JD Required Skills")
        st.info(", ".join(sorted(jd_skills)) if jd_skills else "No skills detected")

    st.divider()

    st.markdown("### 🎯 Matched Skills")
    st.success(", ".join(matched_skills) if matched_skills else "No matched skills")

    st.markdown("### ❌ Skill Gap (Missing Skills)")
    st.error(", ".join(missing_skills) if missing_skills else "No skill gaps found 🎉")

    st.divider()

    # -----------------------------
    # Suggestions
    # -----------------------------
    st.markdown("### 🛠 Resume Improvement Suggestions")
    for s in resume_suggestions(missing_skills):
        st.write("•", s)

    st.markdown("### 📚 Skills You Should Learn")
    if missing_skills:
        for skill in missing_skills:
            st.write("•", skill)
    else:
        st.success("You already meet the job skill requirements!")
