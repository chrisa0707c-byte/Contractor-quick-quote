import streamlit as st
import os
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Set up the visual page title
st.set_page_config(page_title="Quick Quote AI - Beta", page_icon="🏗️")
st.title("🏗️ Quick Quote AI (Beta)")
st.write("Generate professional, client-ready estimates in 30 seconds.")

# --- STEP 1: Data structure for OpenAI ---
class LineItem(BaseModel):
    item_name: str
    quantity: float
    unit: str
    estimated_cost_per_unit: float
    total_item_cost: float

class AIQuoteResponse(BaseModel):
    business_justification: str
    estimated_days_to_complete: int
    materials_list: List[LineItem]
    labor_list: List[LineItem]
    grand_total: float

# --- FUNCTION: Generate PDF Document ---
def generate_pdf(data: AIQuoteResponse, p_type: str, dims: str, zip_c: str):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=24, leading=28, textColor=colors.HexColor('#1E1E1E'), spaceAfter=15)
    section_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor('#0A192F'), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=8)
    
    # Header Branding
    story.append(Paragraph("🏗️ QUICK QUOTE AI - COST ESTIMATE", title_style))
    story.append(Paragraph(f"<b>Project Type:</b> {p_type} | <b>Scope:</b> {dims} | <b>Location Zip:</b> {zip_c}", body_style))
    story.append(Spacer(1, 15))
    
    # Justification Summary
    story.append(Paragraph("Executive Pricing Justification", section_style))
    story.append(Paragraph(data.business_justification, body_style))
    story.append(Paragraph(f"<b>Estimated Days to Complete:</b> {data.estimated_days_to_complete} business days", body_style))
    story.append(Spacer(1, 15))
    
    # Materials Table
    story.append(Paragraph("🪵 Itemized Materials Breakdown", section_style))
    mat_data = [["Material / Item", "Qty", "Unit", "Cost/Unit", "Total"]]
    for item in data.materials_list:
        mat_data.append([item.item_name, str(item.quantity), item.unit, f"${item.estimated_cost_per_unit:.2f}", f"${item.total_item_cost:.2f}"])
    
    t_mat = Table(mat_data, colWidths=[200, 50, 60, 80, 90])
    t_mat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E1E1E')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9F9F9')])
    ]))
    story.append(t_mat)
    story.append(Spacer(1, 15))
    
    # Labor Table
    story.append(Paragraph("🛠️ Regional Labor Breakdown", section_style))
    lab_data = [["Labor Description", "Qty", "Unit", "Rate/Unit", "Total"]]
    for labor in data.labor_list:
        lab_data.append([labor.item_name, str(labor.quantity), labor.unit, f"${labor.estimated_cost_per_unit:.2f}", f"${labor.total_item_cost:.2f}"])
    
    t_lab = Table(lab_data, colWidths=[200, 50, 60, 80, 90])
    t_lab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0A192F')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9F9F9')])
    ]))
    story.append(t_lab)
    story.append(Spacer(1, 20))
    
    # Grand Total Block
    grand_total_style = ParagraphStyle('GrandTotal', parent=styles['Heading2'], fontSize=16, leading=20, textColor=colors.HexColor('#D9534F'), alignment=2)
    story.append(Paragraph(f"GRAND TOTAL ESTIMATE: ${data.grand_total:.2f}", grand_total_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- STEP 3: The Visual Input Form ---
with st.form("quote_form"):
    project_type = st.selectbox("Project Type", ["Roofing", "Painting", "Plumbing", "Drywall", "Flooring", "Deck Construction", "General Handyman"])
    dimensions = st.text_input("Project Size / Scope (e.g., 500 sq ft)")
    materials_requested = st.text_input("Materials Preferred (e.g., Premium Cedar Wood)")
    zip_code = st.text_input("Job Zip Code")
    extra_notes = st.text_input("Extra Notes (Optional)")
    
    submit = st.form_submit_button("Generate Professional Estimate")

# --- STEP 4: Handle AI Processing & Render PDF Action ---
if submit:
    if not dimensions or not zip_code:
        st.error("Please fill out Size and Zip Code.")
    elif not os.environ.get("OPENAI_API_KEY"):
        st.error("API Key missing in cloud setup.")
    else:
        st.write("🔄 Calculating regional rates and compiling cost table...")
        try:
            client = OpenAI()
            system_prompt = "You are an expert construction estimator. Output accurate, professional itemized cost estimates."
            user_prompt = f"Type: {project_type}\nMaterials: {materials_requested}\nScope: {dimensions}\nZip: {zip_code}\nNotes: {extra_notes}"

            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                response_format=AIQuoteResponse,
            )
            # FIXED BY HARDCODING THE [0] LIST ARRAY ASSIGNMENT DIRECTLY HERE:
            st.session_state['data'] = completion.choices[0].message.parsed
            st.session_state['p_type'] = project_type
            st.session_state['dims'] = dimensions
            st.session_state['zip_c'] = zip_code
        except Exception as e:
            st.error(f"Error: {str(e)}")

# If an estimate is loaded in session memory, display it and render the PDF action
if 'data' in st.session_state:
    data = st.session_state['data']
    st.success("🎉 Estimate Complete!")
    st.subheader(f"💰 Grand Total: ${data.grand_total:.2f}")
    
    # THE PDF GENERATION AND DOWNLOAD BUTTON COMPILER
    pdf_file = generate_pdf(data, st.session_state['p_type'], st.session_state['dims'], st.session_state['zip_c'])
    st.download_button(
        label="📥 Download Estimate Profile as PDF",
        data=pdf_file,
        file_name=f"Estimate_{st.session_state['p_type'].replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
    
    st.write(f"**Justification:** {data.business_justification}")
    st.write(f"**Days to Complete:** {data.estimated_days_to_complete} business days")
    
    st.markdown("### 🪵 Materials Itemization")
    for item in data.materials_list:
        st.write(f"• **{item.item_name}**: {item.quantity} {item.unit} @ ${item.estimated_cost_per_unit:.2f}/unit = **${item.total_item_cost:.2f}**")
        
    st.markdown("### 🛠️ Regional Labor Costs")
    for labor in data.labor_list:
        st.write(f"• **{labor.item_name}**: {labor.quantity} {labor.unit} @ ${labor.estimated_cost_per_unit:.2f}/unit = **${labor.total_item_cost:.2f}**")

# --- STEP 5: The Passive Feedback Box ---
st.markdown("---")
st.subheader("💡 Founder Beta Feedback")
st.write("Help me build the ultimate tool for your business. Tell me what features you want next!")

with st.form("feedback_form", clear_on_submit=True):
    contractor_name = st.text_input("Your Name / Company")
    feedback_text = st.text_area("What features or updates do you need? (e.g., custom logo uploader, history tracking)")
    submit_feedback = st.form_submit_button("Submit Anonymous Feedback")

if submit_feedback:
    if not feedback_text:
        st.warning("Please type your feedback before submitting.")
    else:
        with open("user_feedback.txt", "a") as f:
            f.write(f"Company: {contractor_name} | Feedback: {feedback_text}\n")
        st.success("🔥 Feedback submitted directly to the founder! Thank you.")
