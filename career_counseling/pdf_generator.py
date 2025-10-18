"""
Enhanced PDF Report Generator using ReportLab
Professional design with optimized layout and dynamic content
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
import logging

logger = logging.getLogger(__name__)

def generate_pdf_report(user, report, recommendations):
    """
    Generate a professional PDF report with optimized design
    
    Args:
        user: Django User object
        report: AssessmentReport object
        recommendations: QuerySet of CareerRecommendation objects
    
    Returns:
        BytesIO buffer containing PDF data
    """
    try:
        # Create PDF buffer
        pdf_buffer = BytesIO()
        
        # Create PDF document with optimized margins
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            title="Career Assessment Report"
        )
        
        # Container for PDF elements
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom professional styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=8,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            borderPadding=5,
            backColor=colors.HexColor('#F8F9FA')
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            leading=12
        )
        
        bold_style = ParagraphStyle(
            'CustomBold',
            parent=normal_style,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#333333')
        )
        
        # ==================== COVER PAGE ====================
        elements.append(Spacer(1, 1.5*inch))
        
        # Main title
        elements.append(Paragraph("CAREER ASSESSMENT REPORT", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Subtitle
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=normal_style,
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#666666')
        )
        elements.append(Paragraph("Personalized Career Recommendations", subtitle_style))
        elements.append(Spacer(1, 0.8*inch))
        
        # User info box
        user_info_style = ParagraphStyle(
            'UserInfo',
            parent=normal_style,
            alignment=TA_CENTER,
            fontSize=11,
            borderPadding=10,
            backColor=colors.HexColor('#F0F8FF'),
            borderColor=colors.HexColor('#1f4788'),
            borderWidth=1
        )
        
        user_name = user.get_full_name() or user.username
        user_email = user.email if user.email else "Not provided"
        user_info_text = f"""
        <b>Candidate:</b> {user_name}<br/>
        <b>Email:</b> {user_email}<br/>
        <b>Report Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
        <b>Report ID:</b> CR{datetime.now().strftime('%Y%m%d')}{user.id}
        """
        elements.append(Paragraph(user_info_text, user_info_style))
        elements.append(Spacer(1, 0.5*inch))
        
        # Confidential notice
        confidential_style = ParagraphStyle(
            'Confidential',
            parent=normal_style,
            alignment=TA_CENTER,
            fontSize=8,
            textColor=colors.HexColor('#999999')
        )
        elements.append(Paragraph("<i>Confidential Assessment Report - For Personal Use Only</i>", confidential_style))
        
        elements.append(PageBreak())
        
        # ==================== EXECUTIVE SUMMARY ====================
        elements.append(Paragraph("Executive Summary", heading_style))
        
        summary_text = """
        This comprehensive career assessment report provides personalized career recommendations 
        based on your unique combination of skills, interests, personality traits, and professional 
        preferences. The analysis utilizes advanced machine learning algorithms to match your profile 
        with suitable career paths in today's dynamic job market.
        """
        elements.append(Paragraph(summary_text, normal_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Key findings box
        key_findings_style = ParagraphStyle(
            'KeyFindings',
            parent=normal_style,
            backColor=colors.HexColor('#FFF8E1'),
            borderColor=colors.HexColor('#FFC107'),
            borderWidth=1,
            borderPadding=10,
            leftIndent=10,
            rightIndent=10
        )
        
        total_recommendations = len(recommendations)
        top_confidence = max([rec.confidence_score for rec in recommendations]) * 100 if recommendations else 0
        
        key_findings_text = f"""
        <b>Key Findings:</b><br/>
        • {total_recommendations} career paths identified as strong matches<br/>
        • Top recommendation confidence: {top_confidence:.1f}%<br/>
        • Analysis completed: {datetime.now().strftime('%B %d, %Y')}<br/>
        • Assessment methodology: Skills + Interests + Personality analysis
        """
        elements.append(Paragraph(key_findings_text, key_findings_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # ==================== TOP RECOMMENDATIONS ====================
        elements.append(Paragraph("Top Career Recommendations", heading_style))
        
        if recommendations:
            # Build professional recommendations table
            rec_data = [
                ['#', 'Career Path', 'Match Score', 'Key Strengths'],
                ['1', '', '', '']
            ]
            
            # Clear the placeholder row
            rec_data = [['#', 'Career Path', 'Match Score', 'Key Strengths']]
            
            for idx, rec in enumerate(recommendations[:6], 1):
                confidence = f"{int(rec.confidence_score * 100)}%"
                career_title = rec.career_path.title
                
                # Generate dynamic description based on available data
                description = generate_career_description(rec, idx)
                
                rec_data.append([
                    str(idx),
                    career_title,
                    confidence,
                    description
                ])
            
            # Create table with optimized column widths
            rec_table = Table(rec_data, colWidths=[0.4*inch, 1.8*inch, 0.8*inch, 3.0*inch])
            
            # Professional table styling
            rec_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                
                # Data rows
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Rank column
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Score column
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Career column
                ('ALIGN', (3, 1), (3, -1), 'LEFT'),    # Description column
                
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), 
                 [colors.white, colors.HexColor('#f8f9fa')]),
                
                # Grid lines
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#1f4788')),
                
                # Padding
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            
            elements.append(rec_table)
        else:
            elements.append(Paragraph("No career recommendations available.", normal_style))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # ==================== DETAILED ANALYSIS ====================
        elements.append(PageBreak())
        elements.append(Paragraph("Detailed Analysis", heading_style))
        
        # Skills Analysis Section
        elements.append(Paragraph("Skills Assessment", subheading_style))
        skills_text = process_analysis_data(report.skill_analysis, "skills")
        elements.append(Paragraph(skills_text, normal_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # Interests Analysis Section
        elements.append(Paragraph("Interests Profile", subheading_style))
        interests_text = process_analysis_data(report.interest_analysis, "interests")
        elements.append(Paragraph(interests_text, normal_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # Personality Insights Section
        elements.append(Paragraph("Personality Insights", subheading_style))
        personality_text = process_analysis_data(report.personality_insights, "personality")
        elements.append(Paragraph(personality_text, normal_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # ==================== NEXT STEPS ====================
        elements.append(Paragraph("Recommended Next Steps", subheading_style))
        
        next_steps_text = """
        <b>1. Research Top Careers:</b> Explore the recommended career paths in detail<br/>
        <b>2. Skill Development:</b> Identify key skills to develop for your top matches<br/>
        <b>3. Networking:</b> Connect with professionals in your target industries<br/>
        <b>4. Education Planning:</b> Research required education and certifications<br/>
        <b>5. Career Counseling:</b> Schedule a session with a career advisor<br/>
        """
        elements.append(Paragraph(next_steps_text, normal_style))
        
        # ==================== FOOTER ====================
        elements.append(Spacer(1, 0.3*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=normal_style,
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        )
        
        footer_text = """
        <i>This report was generated by CounselBot AI Career Assessment System.<br/>
        For personalized career counseling or additional support, please contact our career advisors.<br/>
        Report generated on: {date}</i>
        """.format(date=datetime.now().strftime('%Y-%m-%d %H:%M'))
        
        elements.append(Paragraph(footer_text, footer_style))
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer
        
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        raise Exception(f"Error generating PDF report: {str(e)}")

def generate_career_description(recommendation, rank):
    """
    Generate dynamic, unique descriptions for each career recommendation
    """
    base_strengths = [
        "strong analytical thinking", "excellent communication skills", 
        "creative problem-solving", "leadership potential", "technical proficiency",
        "attention to detail", "adaptability", "collaborative mindset",
        "strategic thinking", "innovative approach"
    ]
    
    industry_terms = {
        "technology": ["programming", "software development", "IT infrastructure", "digital solutions"],
        "healthcare": ["patient care", "medical knowledge", "healthcare systems", "clinical skills"],
        "business": ["strategic planning", "market analysis", "financial acumen", "management"],
        "creative": ["design thinking", "visual communication", "creative expression", "artistic skills"],
        "education": ["teaching ability", "knowledge sharing", "mentoring", "educational theory"]
    }
    
    # Use the reasoning if available and unique
    if recommendation.reasoning and len(recommendation.reasoning) > 20:
        # Clean up the reasoning text
        reasoning = recommendation.reasoning.strip()
        if not reasoning.startswith("You have strong skills in Communication"):
            return reasoning[:120] + "..." if len(reasoning) > 120 else reasoning
    
    # Fallback: Generate dynamic description based on rank and career title
    career_lower = recommendation.career_path.title.lower()
    
    # Determine industry category
    industry = "general"
    for ind, terms in industry_terms.items():
        if any(term in career_lower for term in terms):
            industry = ind
            break
    
    # Select strengths based on industry and rank
    strength_idx = (rank + hash(recommendation.career_path.title)) % len(base_strengths)
    strength = base_strengths[strength_idx]
    
    descriptions = {
        1: f"Excellent match with your {strength} and overall profile. Shows strong alignment with your core competencies.",
        2: f"Strong potential based on your {strength}. Complements your secondary skill sets effectively.",
        3: f"Good fit leveraging your {strength}. Offers diverse opportunities for professional growth.",
        4: f"Solid option that utilizes your {strength}. Provides stable career progression paths.",
        5: f"Promising alternative that aligns with your {strength}. Worth exploring for variety.",
        6: f"Interesting possibility that matches your {strength}. Consider for long-term development."
    }
    
    return descriptions.get(rank, f"Good career match utilizing your {strength} and professional interests.")

def process_analysis_data(data, data_type):
    """
    Process and format analysis data for PDF display
    """
    if not data:
        return f"No {data_type} data available from the assessment."
    
    try:
        # Handle string data that might be JSON
        if isinstance(data, str):
            data = json.loads(data)
        
        if isinstance(data, dict):
            items = []
            for key, value in list(data.items())[:6]:  # Show top 6 items
                if isinstance(value, (int, float)):
                    items.append(f"• <b>{key}</b>: {value}%")
                else:
                    items.append(f"• <b>{key}</b>: {value}")
            return "<br/>".join(items)
        
        elif isinstance(data, list):
            items = []
            for item in data[:6]:
                if isinstance(item, dict):
                    name = item.get('name', 'Item')
                    score = item.get('score', item.get('value', 'N/A'))
                    items.append(f"• <b>{name}</b>: {score}%")
                else:
                    items.append(f"• {item}")
            return "<br/>".join(items)
        
        else:
            return f"{data_type.capitalize()} data: {str(data)[:200]}..."
            
    except Exception as e:
        logger.warning(f"Error processing {data_type} data: {str(e)}")
        return f"{data_type.capitalize()} analysis completed. Detailed data processing unavailable."