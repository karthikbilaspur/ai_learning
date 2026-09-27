from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(company_name: str, markdown_content: str) -> BytesIO:
    """Converts the Markdown research report into a styled PDF document using ReportLab."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=15
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    story = [
        Paragraph(f"Market Intelligence Report: {company_name}", title_style),
        Spacer(1, 12)
    ]

    # Simple Markdown line parser into ReportLab Flowables
    lines = markdown_content.split('\n')
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        if clean_line.startswith('#'):
            heading_text = clean_line.lstrip('#').strip()
            story.append(Paragraph(f"<b>{heading_text}</b>", styles['Heading2']))
            story.append(Spacer(1, 6))
        else:
            story.append(Paragraph(clean_line, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer