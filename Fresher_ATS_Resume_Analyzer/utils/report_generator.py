"""
PDF ATS Report Generator using ReportLab.
Produces a clean, single-column A4 ATS Compatibility Report ready for download.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_ats_pdf_report(
    candidate_name: str,
    resume_name: str,
    job_title: str,
    analysis_data: dict
) -> bytes:
    """
    Constructs a professional single-column PDF report and returns the raw bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        alignment=TA_LEFT
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569")
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    bold_body = ParagraphStyle(
        "BoldBody",
        parent=body_style,
        fontName="Helvetica-Bold"
    )

    score_style = ParagraphStyle(
        "BigScore",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=30,
        textColor=colors.HexColor("#2563eb"),
        alignment=TA_CENTER
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("Fresher ATS Resume Analyzer", title_style))
    story.append(Paragraph(f"Comprehensive ATS Compatibility & Job Match Report | Generated {datetime.now().strftime('%d %B %Y, %I:%M %p')}", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=12))

    # 2. Metadata Table
    meta_data = [
        [
            Paragraph("<b>Candidate:</b> " + str(candidate_name), body_style),
            Paragraph("<b>Target Role:</b> " + str(job_title), body_style)
        ],
        [
            Paragraph("<b>Resume File:</b> " + str(resume_name), body_style),
            Paragraph("<b>Evaluation Standard:</b> Entry-Level / Fresher ATS Scoring", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[260, 260])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # 3. Overall Scores Card
    final_score = analysis_data.get("final_ats_score", 0.0)
    job_match_pct = analysis_data.get("job_match", {}).get("overall_match_percentage", 0.0)

    score_card_data = [
        [
            Paragraph("ATS COMPATIBILITY SCORE", ParagraphStyle("H1", parent=subtitle_style, alignment=TA_CENTER, fontName="Helvetica-Bold", textColor=colors.HexColor("#1e3a8a"))),
            Paragraph("JOB MATCH SIMILARITY", ParagraphStyle("H2", parent=subtitle_style, alignment=TA_CENTER, fontName="Helvetica-Bold", textColor=colors.HexColor("#065f46")))
        ],
        [
            Paragraph(f"{final_score} / 100", score_style),
            Paragraph(f"{job_match_pct}%", ParagraphStyle("BigScore2", parent=score_style, textColor=colors.HexColor("#059669")))
        ],
        [
            Paragraph("Application-generated 100-pt compatibility score", ParagraphStyle("Sub1", parent=subtitle_style, alignment=TA_CENTER, fontSize=8)),
            Paragraph("Similarity metric across required skills & text", ParagraphStyle("Sub2", parent=subtitle_style, alignment=TA_CENTER, fontSize=8))
        ]
    ]
    score_table = Table(score_card_data, colWidths=[260, 260])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#eff6ff")),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor("#ecfdf5")),
        ('BOX', (0, 0), (0, -1), 1, colors.HexColor("#93c5fd")),
        ('BOX', (1, 0), (1, -1), 1, colors.HexColor("#a7f3d0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 14))

    # 4. Exact ATS Score Breakdown (100 Points)
    story.append(Paragraph("1. ATS Compatibility Score Breakdown", heading_style))
    sb = analysis_data.get("score_breakdown", {})
    bd_data = [
        [Paragraph("<b>Component</b>", bold_body), Paragraph("<b>Max Points</b>", bold_body), Paragraph("<b>Awarded Score</b>", bold_body), Paragraph("<b>Status / Evaluation</b>", bold_body)],
        [Paragraph("Keyword Match", body_style), "30 pts", f"{sb.get('keyword_match', {}).get('score', 0)} pts", f"{sb.get('keyword_match', {}).get('pct', 0)}% JD keywords covered"],
        [Paragraph("Skills Match", body_style), "20 pts", f"{sb.get('skills_match', {}).get('score', 0)} pts", f"{sb.get('skills_match', {}).get('pct', 0)}% technical skills matched"],
        [Paragraph("Resume Sections", body_style), "15 pts", f"{sb.get('resume_sections', {}).get('score', 0)} pts", "Standard fresher section headers"],
        [Paragraph("Formatting & Layout", body_style), "15 pts", f"{sb.get('formatting', {}).get('score', 0)} pts", "Clean single-column parsing flow"],
        [Paragraph("Job Relevance", body_style), "10 pts", f"{sb.get('job_relevance', {}).get('score', 0)} pts", "Project, training & summary relevance"],
        [Paragraph("Contact Information", body_style), "10 pts", f"{sb.get('contact_information', {}).get('score', 0)} pts", "Name, email, phone, links detected"],
        [Paragraph("<b>TOTAL ATS COMPATIBILITY SCORE</b>", bold_body), Paragraph("<b>100 pts</b>", bold_body), Paragraph(f"<b>{final_score} pts</b>", bold_body), Paragraph(f"<b>{round(final_score, 1)}% Overall</b>", bold_body)]
    ]
    bd_table = Table(bd_data, colWidths=[180, 75, 85, 180])
    bd_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#f8fafc")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(bd_table)
    story.append(Spacer(1, 12))

    # 5. Keywords & Skills Analysis
    story.append(Paragraph("2. Keywords & Skills Analysis", heading_style))
    matched_kws = analysis_data.get("keywords", {}).get("matched_keywords", [])
    missing_kws = analysis_data.get("keywords", {}).get("missing_keywords", [])
    req_skills = analysis_data.get("skills", {}).get("required_skills", [])
    found_skills = analysis_data.get("skills", {}).get("resume_skills", [])

    matched_kw_str = ", ".join(matched_kws) if matched_kws else "None detected"
    missing_kw_str = ", ".join(missing_kws) if missing_kws else "None detected"
    found_skills_str = ", ".join(found_skills) if found_skills else "None detected"

    kw_summary_data = [
        [Paragraph("<b>Matched Keywords:</b>", bold_body), Paragraph(f"<font color='#059669'>[OK] {matched_kw_str}</font>", body_style)],
        [Paragraph("<b>Missing Keywords:</b>", bold_body), Paragraph(f"<font color='#d97706'>[!] {missing_kw_str}</font>", body_style)],
        [Paragraph("<b>Skills Detected in Resume:</b>", bold_body), Paragraph(found_skills_str, body_style)]
    ]
    kw_table = Table(kw_summary_data, colWidths=[140, 380])
    kw_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
    ]))
    story.append(kw_table)
    story.append(Spacer(1, 12))

    # 6. Fresher Resume Checklist
    story.append(Paragraph("3. Fresher Resume Checklist", heading_style))
    checklist = analysis_data.get("fresher_checklist", [])
    cl_rows = []
    for item in checklist:
        mark = "[YES] Present" if item["status"] else "[--] Missing"
        mark_color = "#059669" if item["status"] else "#dc2626"
        cl_rows.append([
            Paragraph(f"<b>{item['label']}</b>", bold_body),
            Paragraph(f"<font color='{mark_color}'><b>{mark}</b></font>", body_style),
            Paragraph(item["tip"], body_style)
        ])
    cl_table = Table(cl_rows, colWidths=[140, 80, 300])
    cl_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(cl_table)
    story.append(Spacer(1, 12))

    # 7. Actionable Improvement Suggestions
    story.append(Paragraph("4. Actionable Improvement Suggestions", heading_style))
    suggestions = analysis_data.get("improvement_suggestions", [])
    for idx, s in enumerate(suggestions, 1):
        p_text = f"<b>{idx}.</b> {s}"
        story.append(Paragraph(p_text, body_style))
        story.append(Spacer(1, 4))

    # 8. Disclaimer Footer
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    disclaimer = (
        "<b>Notice:</b> This report is generated by Fresher ATS Resume Analyzer based on transparent NLP heuristics "
        "and rule-based scoring (Keyword Match 30%, Skills 20%, Sections 15%, Formatting 15%, Relevance 10%, Contact 10%). "
        "It provides actionable resume optimization guidance and does not guarantee employer hiring or selection."
    )
    story.append(Paragraph(disclaimer, ParagraphStyle("Disc", parent=subtitle_style, fontSize=7.5, leading=10)))

    # Build PDF document
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
