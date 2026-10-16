"""
Generate Realistic Sample Resumes (PDF & DOCX) for testing the ATS Web Application.

Creates:
1. sample_resumes/alex_python_developer.docx  (Strong match for Python Developer)
2. sample_resumes/sarah_data_scientist.pdf   (Strong match for Data Science / Python)
3. sample_resumes/david_marketing_manager.pdf (Low match candidate to test missing skills)
"""

import os
import docx
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_resumes")
os.makedirs(SAMPLE_DIR, exist_ok=True)


def create_alex_docx():
    """Create DOCX resume for Alex Johnson (Junior Python Developer - High Match)."""
    filepath = os.path.join(SAMPLE_DIR, "alex_python_developer.docx")
    doc = docx.Document()
    
    # Title / Name
    doc.add_heading("Alex Johnson", level=0)
    p_contact = doc.add_paragraph("alex.johnson@example.com | +1 (555) 014-2391 | San Francisco, CA | github.com/alexj-dev")
    
    # Summary
    doc.add_heading("Professional Summary", level=1)
    doc.add_paragraph(
        "Enthusiastic Junior Python Developer with 1.5 years of hands-on experience developing web applications "
        "using Python, Flask, and SQLite. Skilled in crafting responsive frontend interfaces with HTML5, CSS3, and JavaScript. "
        "Passionate about writing clean code, building REST APIs, and collaborating with cross-functional teams in an Agile environment."
    )
    
    # Technical Skills
    doc.add_heading("Technical Skills", level=1)
    doc.add_paragraph("• Languages: Python, JavaScript, SQL, HTML5, CSS3")
    doc.add_paragraph("• Frameworks & Libraries: Flask, Jinja, Pandas, NumPy, Scikit-learn, Bootstrap")
    doc.add_paragraph("• Databases: SQLite, PostgreSQL, MySQL")
    doc.add_paragraph("• Tools & Methodologies: Git, GitHub, REST APIs, Unit Testing, Linux, Docker, Agile/Scrum")
    
    # Experience
    doc.add_heading("Work Experience", level=1)
    doc.add_heading("Junior Software Developer | TechNova Solutions (2023 - Present)", level=2)
    doc.add_paragraph("• Developed and deployed backend REST APIs using Python and Flask, reducing response times by 20%.")
    doc.add_paragraph("• Built dynamic web user interfaces with HTML, CSS, and modern JavaScript.")
    doc.add_paragraph("• Integrated SQLite and PostgreSQL databases, writing optimized SQL queries and managing migrations.")
    doc.add_paragraph("• Processed large tabular client datasets using Pandas for automated analytics reporting.")
    doc.add_paragraph("• Utilized Git and GitHub for branch management, code reviews, and continuous integration.")
    
    # Education
    doc.add_heading("Education", level=1)
    doc.add_paragraph("B.S. in Computer Science | State University (Graduated 2023)")
    
    doc.save(filepath)
    print(f"Created DOCX resume: {filepath}")


def create_sarah_pdf():
    """Create PDF resume for Sarah Chen (Data Scientist - Good Match)."""
    filepath = os.path.join(SAMPLE_DIR, "sarah_data_scientist.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#0f172a'))
    h1_style = ParagraphStyle('H1Style', parent=styles['Heading2'], fontSize=13, leading=17, textColor=colors.HexColor('#2563eb'), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#334155'))
    contact_style = ParagraphStyle('ContactStyle', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#64748b'))
    
    elements = [
        Paragraph("Sarah Chen", title_style),
        Paragraph("sarah.chen@example.com | (555) 234-8890 | Boston, MA | linkedin.com/in/sarahchen-ds", contact_style),
        Spacer(1, 10),
        
        Paragraph("PROFESSIONAL SUMMARY", h1_style),
        Paragraph(
            "Analytical Data Scientist and Python Developer with proven expertise in data analysis, machine learning algorithms, "
            "and predictive modeling using Pandas, NumPy, and Scikit-learn. Experienced in querying databases using SQL and building "
            "Python data visualization applications.", body_style
        ),
        Spacer(1, 6),
        
        Paragraph("CORE SKILLS & TECHNOLOGIES", h1_style),
        Paragraph("<b>Languages & Tools:</b> Python, SQL, Git, GitHub, Linux, Docker, Jupyter", body_style),
        Paragraph("<b>Data & ML:</b> Pandas, NumPy, Scikit-learn, Statistics, Machine Learning, Data Analysis", body_style),
        Paragraph("<b>Web & Databases:</b> Flask, SQLite, PostgreSQL, REST APIs", body_style),
        Spacer(1, 6),
        
        Paragraph("WORK EXPERIENCE", h1_style),
        Paragraph("<b>Associate Data Scientist</b> &bull; DataSphere Analytics (2022 - Present)", body_style),
        Paragraph("&bull; Built supervised classification and regression pipelines using Python and Scikit-learn.", body_style),
        Paragraph("&bull; Analyzed millions of rows with Pandas and executed complex SQL queries against PostgreSQL databases.", body_style),
        Paragraph("&bull; Created internal reporting dashboards with Python, Flask, and HTML/CSS.", body_style),
        Paragraph("&bull; Maintained version control across multiple analytics projects using Git and GitHub.", body_style),
        Spacer(1, 6),
        
        Paragraph("EDUCATION", h1_style),
        Paragraph("<b>B.S. in Data Science and Statistics</b> &bull; University of Technology (2022)", body_style)
    ]
    
    doc.build(elements)
    print(f"Created PDF resume: {filepath}")


def create_david_pdf():
    """Create PDF resume for David Miller (Marketing Specialist - Low Match to test missing skills)."""
    filepath = os.path.join(SAMPLE_DIR, "david_marketing_specialist.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#0f172a'))
    h1_style = ParagraphStyle('H1Style', parent=styles['Heading2'], fontSize=13, leading=17, textColor=colors.HexColor('#2563eb'), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#334155'))
    contact_style = ParagraphStyle('ContactStyle', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#64748b'))
    
    elements = [
        Paragraph("David Miller", title_style),
        Paragraph("david.miller@example.com | (555) 987-6543 | Chicago, IL", contact_style),
        Spacer(1, 10),
        
        Paragraph("PROFESSIONAL SUMMARY", h1_style),
        Paragraph(
            "Results-driven Digital Marketing and Brand Strategy Specialist with 4 years of experience leading "
            "content creation, search engine optimization (SEO), social media campaigns, and brand partnerships. "
            "Expert in driving organic traffic, managing advertising budgets, and organizing corporate events.", body_style
        ),
        Spacer(1, 6),
        
        Paragraph("CORE SKILLS", h1_style),
        Paragraph("Digital Marketing, SEO, SEM, Content Strategy, Social Media Management, Copywriting, Google Ads, Communication, Leadership", body_style),
        Spacer(1, 6),
        
        Paragraph("WORK EXPERIENCE", h1_style),
        Paragraph("<b>Marketing Specialist</b> &bull; Creative Pulse Agency (2021 - Present)", body_style),
        Paragraph("&bull; Managed inbound digital marketing campaigns across Google Ads, Facebook, and LinkedIn.", body_style),
        Paragraph("&bull; Increased organic website traffic by 45% through keyword research and SEO content optimization.", body_style),
        Paragraph("&bull; Collaborated with design and sales teams to produce customer case studies and email newsletters.", body_style),
        Spacer(1, 6),
        
        Paragraph("EDUCATION", h1_style),
        Paragraph("<b>B.A. in Communications &amp; Marketing</b> &bull; Midwest College (2021)", body_style)
    ]
    
    doc.build(elements)
    print(f"Created PDF resume: {filepath}")


if __name__ == "__main__":
    print("Generating sample resumes...")
    create_alex_docx()
    create_sarah_pdf()
    create_david_pdf()
    print("All sample resumes created successfully in 'sample_resumes/' folder!")
