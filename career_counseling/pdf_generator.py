"""
PDF Report Generator using ReportLab
Pure Python PDF generation without external system dependencies
"""

from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import json


def generate_pdf_report(user, report, recommendations):
    """
    Generate a professional PDF report using ReportLab
    
    Args:
        user: Django User object
        report: AssessmentReport object
        recommendations: QuerySet of CareerRecommendation objects
    
    Returns:
        BytesIO buffer containing PDF data
    """
    # Create PDF buffer
    pdf_buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        title="Career Assessment Report"
    )
    
    # Container for PDF elements
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )
    
    # ==================== TITLE SECTION ====================
    elements.append(Paragraph("CAREER ASSESSMENT REPORT", title_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # User info
    user_info = f"<b>Name:</b> {user.get_full_name() or user.username} | <b>Date:</b> {datetime.now().strftime('%B %d, %Y')}"
    elements.append(Paragraph(user_info, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # ==================== EXECUTIVE SUMMARY ====================
    elements.append(Paragraph("Executive Summary", heading_style))
    
    summary_text = "This comprehensive career assessment report provides personalized career recommendations based on your skills, interests, and personality traits. The recommendations below are ranked by match confidence score."
    elements.append(Paragraph(summary_text, normal_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # ==================== RECOMMENDATIONS TABLE ====================
    elements.append(Paragraph("Top Career Recommendations", heading_style))
    
    # Build recommendations table
    rec_data = [['Career Path', 'Confidence', 'Description']]
    
    for idx, rec in enumerate(recommendations[:5], 1):
        confidence = f"{int(rec.confidence_score * 100)}%"
        career_title = rec.career_path.title
        description = rec.reasoning[:80] + "..." if len(rec.reasoning) > 80 else rec.reasoning
        
        rec_data.append([career_title, confidence, description])
    
    # Create recommendations table
    rec_table = Table(rec_data, colWidths=[2.5*inch, 1*inch, 1.5*inch])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(rec_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # ==================== SKILLS ANALYSIS ====================
    elements.append(PageBreak())
    elements.append(Paragraph("Skills Analysis", heading_style))
    
    try:
        skill_data = report.skill_analysis
        if isinstance(skill_data, str):
            skill_data = json.loads(skill_data)
        
        if skill_data:
            skills_text = "<b>Identified Skills:</b><br/>"
            if isinstance(skill_data, dict):
                for skill, score in list(skill_data.items())[:8]:
                    skills_text += f" {skill}: {score}%<br/>"
            elif isinstance(skill_data, list):
                for item in skill_data[:8]:
                    if isinstance(item, dict):
                        skills_text += f" {item.get('name', 'Skill')}: {item.get('score', 0)}%<br/>"
                    else:
                        skills_text += f" {item}<br/>"
            
            elements.append(Paragraph(skills_text, normal_style))
        else:
            elements.append(Paragraph("No specific skills data available.", normal_style))
    except Exception as e:
        elements.append(Paragraph(f"Skills data: {str(skill_data)[:200]}", normal_style))
    
    elements.append(Spacer(1, 0.15*inch))
    
    # ==================== INTERESTS ANALYSIS ====================
    elements.append(Paragraph("Interests Analysis", heading_style))
    
    try:
        interest_data = report.interest_analysis
        if isinstance(interest_data, str):
            interest_data = json.loads(interest_data)
        
        if interest_data:
            interests_text = "<b>Identified Interests:</b><br/>"
            if isinstance(interest_data, dict):
                for interest, score in list(interest_data.items())[:8]:
                    interests_text += f" {interest}: {score}%<br/>"
            elif isinstance(interest_data, list):
                for item in interest_data[:8]:
                    if isinstance(item, dict):
                        interests_text += f" {item.get('name', 'Interest')}: {item.get('score', 0)}%<br/>"
                    else:
                        interests_text += f" {item}<br/>"
            
            elements.append(Paragraph(interests_text, normal_style))
        else:
            elements.append(Paragraph("No specific interests data available.", normal_style))
    except Exception as e:
        elements.append(Paragraph(f"Interests data: {str(interest_data)[:200]}", normal_style))
    
    elements.append(Spacer(1, 0.15*inch))
    
    # ==================== PERSONALITY INSIGHTS ====================
    elements.append(Paragraph("Personality Insights", heading_style))
    
    try:
        personality_data = report.personality_insights
        if isinstance(personality_data, str):
            personality_data = json.loads(personality_data)
        
        if personality_data:
            personality_text = "<b>Personality Traits:</b><br/>"
            if isinstance(personality_data, dict):
                for trait, value in list(personality_data.items())[:8]:
                    personality_text += f" {trait}: {value}<br/>"
            elif isinstance(personality_data, list):
                for item in personality_data[:8]:
                    if isinstance(item, dict):
                        personality_text += f" {item.get('trait', 'Trait')}: {item.get('value', 'N/A')}<br/>"
                    else:
                        personality_text += f" {item}<br/>"
            
            elements.append(Paragraph(personality_text, normal_style))
        else:
            elements.append(Paragraph("No specific personality data available.", normal_style))
    except Exception as e:
        elements.append(Paragraph(f"Personality data: {str(personality_data)[:200]}", normal_style))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # ==================== FOOTER ====================
    elements.append(Spacer(1, 0.2*inch))
    footer_text = "<i>This report was generated automatically based on your assessment responses. For more information or career counseling, please contact our support team.</i>"
    elements.append(Paragraph(footer_text, normal_style))
    
    # Build PDF
    try:
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer
    except Exception as e:
        raise Exception(f"Error building PDF: {str(e)}")
