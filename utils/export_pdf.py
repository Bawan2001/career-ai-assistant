import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(state_data: dict) -> bytes:
    """
    Generates a professional PDF report containing CV Analysis, Job Match score,
    Career recommendations, and Reflection critique.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        alignment=1, # Center
        spaceAfter=12
    )

    heading2_style = ParagraphStyle(
        'DocHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )

    elements = []

    # Title
    elements.append(Paragraph("AI Career Guidance & CV Analysis Report", title_style))
    elements.append(Paragraph("Horizon Campus - IT41043 Intelligent Systems Project", ParagraphStyle('Sub', parent=body_style, alignment=1, textColor=colors.HexColor('#64748B'))))
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=15))

    cv_out = state_data.get("cv_analysis_output", {})
    job_out = state_data.get("job_matching_output", {})
    career_out = state_data.get("career_recommendations_output", {})
    reflection_out = state_data.get("reflection_output", {})

    # Section 1: Scores Overview Table
    elements.append(Paragraph("1. Executive Performance Summary", heading2_style))
    
    summary_table_data = [
        ["Metric Category", "Score / Metric", "Status"],
        ["ATS CV Score", f"{cv_out.get('score', 0)} / 100", "Analyzed"],
        ["Target Job Match", f"{job_out.get('match_percentage', 0)} %", job_out.get("role_alignment_level", "Evaluated")],
        ["Quality Audit Score", f"{reflection_out.get('quality_score', 90)} / 100", "Passed Gate" if reflection_out.get("passed_quality_gate") else "Reviewed"]
    ]

    table = Table(summary_table_data, colWidths=[200, 150, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))

    # Section 2: CV Flaws & Improvements
    elements.append(Paragraph("2. CV Improvement Recommendations", heading2_style))
    for imp in cv_out.get("actionable_improvements", []):
        elements.append(Paragraph(f"• {imp}", body_style))
    elements.append(Spacer(1, 12))

    # Section 3: Skill Gaps
    if job_out.get("critical_missing_skills"):
        elements.append(Paragraph("3. Target Job Skill Gap Analysis", heading2_style))
        elements.append(Paragraph(f"<b>Missing Target Skills:</b> {', '.join(job_out.get('critical_missing_skills', []))}", body_style))
        elements.append(Spacer(1, 12))

    # Section 4: Learning Roadmap
    elements.append(Paragraph("4. Recommended Learning Roadmap", heading2_style))
    for phase in career_out.get("learning_roadmap", []):
        phase_name = phase.get("phase", "Learning Phase")
        focus = phase.get("focus", "")
        elements.append(Paragraph(f"<b>{phase_name}:</b> {focus}", body_style))
        for item in phase.get("action_items", []):
            elements.append(Paragraph(f"  - {item}", body_style))
        elements.append(Spacer(1, 6))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
