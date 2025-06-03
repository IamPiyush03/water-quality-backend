from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import io

def generate_water_quality_report(measurement_data, prediction_data, recommendations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph("Water Quality Analysis Report", title_style))
    story.append(Spacer(1, 12))

    # Date and Time
    date_style = styles["Normal"]
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
    story.append(Spacer(1, 20))

    # Water Quality Index
    wqi_style = ParagraphStyle(
        'WQIStyle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12
    )
    story.append(Paragraph("Water Quality Index", wqi_style))
    story.append(Paragraph(f"WQI Value: {prediction_data['wqi_value']:.2f}", styles["Normal"]))
    story.append(Paragraph(f"Quality Category: {prediction_data['quality_category']}", styles["Normal"]))
    story.append(Paragraph(f"Potability: {'Potable' if prediction_data['is_potable'] else 'Not Potable'}", styles["Normal"]))
    story.append(Spacer(1, 20))

    # Parameters Table
    story.append(Paragraph("Measured Parameters", wqi_style))
    data = [["Parameter", "Value", "Unit"]]
    parameters = {
        "Temperature": ("temperature", "°C"),
        "Dissolved Oxygen": ("dissolved_oxygen", "mg/L"),
        "pH": ("ph", ""),
        "Conductivity": ("conductivity", "µS/cm"),
        "BOD": ("bod", "mg/L"),
        "Nitrate": ("nitrate", "mg/L"),
        "Fecal Coliform": ("fecal_coliform", "MPN/100ml"),
        "Total Coliform": ("total_coliform", "MPN/100ml")
    }
    
    for param_name, (param_key, unit) in parameters.items():
        value = measurement_data[param_key]
        data.append([param_name, f"{value:.2f}", unit])

    table = Table(data, colWidths=[2*inch, 1.5*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    # Recommendations
    story.append(Paragraph("Recommendations", wqi_style))
    for category, recs in recommendations.items():
        if recs:  # Only show categories that have recommendations
            story.append(Paragraph(category.replace('_', ' ').title(), styles["Heading3"]))
            for rec in recs:
                story.append(Paragraph(f"• {rec['description']}", styles["Normal"]))
                if rec.get('health_implications'):
                    story.append(Paragraph("Health Implications:", styles["Normal"]))
                    for imp in rec['health_implications']:
                        story.append(Paragraph(f"  - {imp}", styles["Normal"]))
                story.append(Spacer(1, 6))
            story.append(Spacer(1, 12))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer 