from flask import Blueprint, request, jsonify, send_file, current_app
from ..auth import auth_required
from ..database import get_db
import os
import json
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from ..groq_ai import call_groq_ai

report_bp = Blueprint('report', __name__)

def call_groq_for_conclusion(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT * FROM business_strategies WHERE user_id = ? ORDER BY created_at DESC LIMIT 3", (user_id,))
    strategies = cursor.fetchall()
    strategy_summary = ""
    for strategy in strategies:
        strategy_summary += f"Strategy for {strategy['business_type']} in {strategy['location_name']}: {strategy['strategy'][:200]}...\n"
    prompt = f"""
    Create a conclusion for a market research report for {user['business_name'] or user['username']}.
    Recent strategies analyzed:
    {strategy_summary}
    The conclusion should:
    1. Summarize key insights from the data
    2. Provide 2-3 actionable recommendations for next steps
    3. Highlight potential risks and opportunities
    4. Be professional but conversational in tone
    5. Be around 250-300 words
    """
    return call_groq_ai(prompt, system_message="You are a market research expert who creates insightful report conclusions.")

def generate_pdf_report(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    title_style = styles['Title']
    elements.append(Paragraph(f"Market Research Report for {user['business_name'] or user['username']}", title_style))
    elements.append(Spacer(1, 12))
    date_style = styles['Normal']
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
    elements.append(Spacer(1, 24))
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        leading=16,
        spaceAfter=10
    )
    cursor.execute("SELECT * FROM business_strategies WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    strategies = cursor.fetchall()
    if strategies:
        elements.append(Paragraph("Business Strategies", section_style))
        elements.append(Spacer(1, 12))
        for strategy in strategies:
            elements.append(Paragraph(f"Strategy for {strategy['business_type']} in {strategy['location_name']}", styles['Heading3']))
            elements.append(Paragraph(strategy['strategy'], styles['Normal']))
            elements.append(Spacer(1, 12))
            if strategy['trend_data']:
                trend_data = json.loads(strategy['trend_data'])
                elements.append(Paragraph("Market Trends:", styles['Heading4']))
                if 'top_categories' in trend_data:
                    elements.append(Paragraph("Top Business Categories:", styles['Heading4']))
                    top_categories = trend_data['top_categories']
                    data = [[cat, count] for cat, count in top_categories]
                    if data:
                        table = Table([['Category', 'Count']] + data, colWidths=[300, 100])
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('BOX', (0, 0), (-1, -1), 1, colors.black),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        elements.append(table)
                        elements.append(Spacer(1, 12))
            if strategy['competitor_data']:
                competitor_data = json.loads(strategy['competitor_data'])
                elements.append(Paragraph("Competitor Analysis:", styles['Heading4']))
                elements.append(Paragraph(f"Total Competitors: {competitor_data.get('total', 0)}", styles['Normal']))
                elements.append(Paragraph(f"Average Rating: {competitor_data.get('avg_rating', 0)}", styles['Normal']))
                elements.append(Paragraph(f"Average Reviews: {competitor_data.get('avg_reviews', 0)}", styles['Normal']))
                elements.append(Spacer(1, 12))
            elements.append(Spacer(1, 24))
    cursor.execute("SELECT * FROM heatmap_data WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    heatmaps = cursor.fetchall()
    if heatmaps:
        elements.append(Paragraph("Heatmap Analysis", section_style))
        elements.append(Spacer(1, 12))
        for heatmap in heatmaps:
            elements.append(Paragraph(f"Heatmap for {heatmap['category']} in {heatmap['location']}", styles['Heading3']))
            heatmap_data = json.loads(heatmap['heatmap_data'])
            elements.append(Paragraph(f"Number of Locations: {heatmap_data.get('count', 0)}", styles['Normal']))
            elements.append(Paragraph(f"Center Coordinates: {heatmap_data.get('center', {})}", styles['Normal']))
            elements.append(Spacer(1, 12))
    cursor.execute("SELECT * FROM landmark_data WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    landmarks = cursor.fetchall()
    if landmarks:
        elements.append(Paragraph("Landmark Analysis", section_style))
        elements.append(Spacer(1, 12))
        for landmark in landmarks:
            elements.append(Paragraph(f"Landmark Analysis for {landmark['business']} in {landmark['location']}", styles['Heading3']))
            if landmark['landmark_data']:
                landmark_data = json.loads(landmark['landmark_data'])
                if 'hostels' in landmark_data:
                    elements.append(Paragraph("Nearby Hostels:", styles['Heading4']))
                    for hostel in landmark_data['hostels']:
                        elements.append(Paragraph(f"• {hostel}", styles['Normal']))
                    elements.append(Spacer(1, 6))
                if 'schools' in landmark_data:
                    elements.append(Paragraph("Nearby Schools:", styles['Heading4']))
                    for school in landmark_data['schools']:
                        elements.append(Paragraph(f"• {school}", styles['Normal']))
                    elements.append(Spacer(1, 6))
                if 'apartments' in landmark_data:
                    elements.append(Paragraph("Nearby Apartments:", styles['Heading4']))
                    for apartment in landmark_data['apartments']:
                        elements.append(Paragraph(f"• {apartment}", styles['Normal']))
                    elements.append(Spacer(1, 6))
            elements.append(Paragraph("Recommendation:", styles['Heading4']))
            elements.append(Paragraph(landmark['recommendation'], styles['Normal']))
            elements.append(Spacer(1, 12))
    elements.append(Paragraph("Conclusion", section_style))
    elements.append(Spacer(1, 12))
    conclusion_text = call_groq_for_conclusion(user_id)
    elements.append(Paragraph(conclusion_text, styles['Normal']))
    doc.build(elements)
    pdf_content = buffer.getvalue()
    buffer.close()
    filename = f"market_research_report_{user_id}_{int(datetime.now().timestamp())}.pdf"
    file_path = os.path.join("reports", filename)
    os.makedirs("reports", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(pdf_content)
    cursor.execute(
        "INSERT INTO generated_reports (user_id, report_name, report_path) VALUES (?, ?, ?)",
        (user_id, f"Market Research Report {datetime.now().strftime('%Y-%m-%d')}", file_path)
    )
    db.commit()
    return file_path

@report_bp.route('/generate-report', methods=['POST'])
@auth_required
def generate_report():
    try:
        user_id = request.user_id
        file_path = generate_pdf_report(user_id)
        return jsonify({
            "message": "Report generated successfully",
            "report_path": file_path
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route('/download-report/<int:report_id>', methods=['GET'])
def download_report(report_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM generated_reports WHERE id = ?", (report_id,))
        report = cursor.fetchone()
        if not report:
            return jsonify({"error": "Report not found or unauthorized"}), 404
        return send_file(report['report_path'], as_attachment=True, download_name=f"{report['report_name']}.pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@report_bp.route('/reports', methods=['GET'])
@auth_required
def list_reports():
    try:
        user_id = request.user_id
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM generated_reports WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        reports = []
        for row in cursor.fetchall():
            reports.append({
                "id": row['id'],
                "report_name": row['report_name'],
                "created_at": row['created_at']
            })
        return jsonify({
            "total": len(reports),
            "reports": reports
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
