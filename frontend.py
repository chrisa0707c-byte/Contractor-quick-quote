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

# Set up the visual page config
st.set_page_config(page_title="Quick Quote AI - Beta", page_icon="🏗️", layout="wide")

# --- STEP 1: Define Navigation Sidebar ---
st.sidebar.image("https://icons8.com", width=80)
st.sidebar.title("Quick Quote AI")
st.sidebar.write("*The Driveway Sales Weapon for Professional Contractors.*")
st.sidebar.markdown("---")

# Navigation panels
page_selection = st.sidebar.radio("Navigate Enterprise Console", ["🏠 Company Overview", "🏗️ AI Estimate Engine", "💳 Beta Licensing"])

# --- SHARED DATA HOOKS FOR OPENAI ---
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

def generate_pdf(data: AIQuoteResponse, p_type: str, dims: str, zip_c: str):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=24, leading=28, textColor=colors.HexColor('#1E1E1E'), spaceAfter=15)
    section_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor('#0A192F'), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=8)
    
    story.append(Paragraph("🏗️ QUICK QUOTE AI - COST ESTIMATE", title_style))
    story.append(Paragraph(f"<b>Project Type:</b> {p_type} | <b>Scope:</b> {dims} | <b>Location Zip:</b> {zip_c}", body_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Executive Pricing Justification", section_style))
    story.append(Paragraph(data.business_justification, body_style))
    story.append(Paragraph(f"<b>Estimated Days to Complete:</b> {data.estimated_days_to_complete} business days", body_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("🪵 Itemized Materials Breakdown", section_style))
    mat_data = [["Material / Item", "Qty", "Unit", "Cost/Unit", "Total"]]
    for item in data.materials_list:
        mat_data.append([item.item_name, str(item.quantity), item.unit, f"${item.estimated_cost_per_unit:.2f}", f"${item.total_item_cost:.2f}"])
    t_mat = Table(mat_data, colWidths=[200, 50, 60, 80, 80])
    t_mat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E1E1E')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9F9F9')])
    ]))
    story.append(t_mat)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("🛠️ Regional Labor Breakdown", section_style))
    lab_data = [["Labor Description", "Qty", "Unit", "Rate/Unit", "Total"]]
    for labor in data.labor_list:
        lab_data.append([labor.item_name, str(labor.quantity), labor.unit, f"${labor.estimated_cost_per_unit:.2f}", f"${labor.total_item_cost:.2f}"])
    t_lab = Table(lab_data, colWidths=[200, 50, 60, 80, 80])
    t_lab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0A192F')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9F9F9')])
    ]))
    story.append(t_lab)
    story.append(Spacer(1, 20))
    
    grand_total_style = ParagraphStyle('GrandTotal', parent=styles['Heading2'], fontSize=16, leading=20, textColor=colors.HexColor('#D9534F'), alignment=2)
    story.append(Paragraph(f"GRAND TOTAL ESTIMATE: ${data.grand_total:.2f}", grand_total_style))
    doc.build(story)
    buffer.seek(0)
    return buffer

# =========================================================
# SCREEN 1: COMPANY OVERVIEW & INQUIRY BOT
# =========================================================
if page_selection == "🏠 Company Overview":
    st.title("🏗️ Stop Losing Construction Deals to Slow Estimates")
    st.markdown("### Close residential clients directly from the driveway in under 30 seconds.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### ⚡ 30-Second Quotes")
        st.write("Ditch evening spreadsheet paperwork. Type basic dimensions right at the job site and let regional AI models construct market-rate breakdowns instantly.")
    with col2:
        st.markdown("### 🧾 Zero Speculation")
        st.write("Build massive customer trust. Hand your client a transparently itemized material and labor breakdown that removes price haggling completely.")
    with col3:
        st.markdown("### 📥 Instant PDF Delivery")
        st.write("Generate professional proposals instantly. Click one button to compile and text or email a polished quote before your competitors even open their laptops.")
        
    st.markdown("---")
    
    # THE BILLION-DOLLAR CUSTOMER INQUIRY SUPPORT BOT FEATURE
    st.subheader("🤖 Client Lead Generator Bot (Beta Preview)")
    st.write("Frame this bot on your corporate homepage. Let clients ask questions and submit job requests that parse directly to your crew.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your automated project assistant. Tell me about your property layout or what trade work you need done, and I will draft a raw request for the project manager."}]
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if bot_input := st.chat_input("Ask a question or describe your project scope here..."):
        st.session_state.messages.append({"role": "user", "content": bot_input})
        with st.chat_message("user"):
            st.write(bot_input)
            
        try:
            client = OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a customer service assistant for a top-tier general contracting firm. Be professional, friendly, and guide them to provide dimensions or zip codes so the manager can follow up. Summarize their details efficiently."},
                    *st.session_state.messages
                ]
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.write(reply)
        except Exception as e:
            st.error(f"Bot Connection Offline: {str(e)}")

# =========================================================
# SCREEN 2: THE core AI CALCULATION MACHINE
# =========================================================
elif page_selection == "🏗️ AI Estimate Engine":
    st.title("🏗️ Quick Quote AI Estimation Console")
    st.write("Input job parameters below to generate itemized transparent metrics.")
    
    with st.form("quote_form"):
        project_type = st.selectbox("Project Type", ["Roofing", "Painting", "Plumbing", "Drywall", "Flooring", "Deck Construction", "General Handyman"])
        dimensions = st.text_input("Project Size / Scope (e.g., 500 sq ft)")
        materials_requested = st.text_input("Materials Preferred (e.g., Premium Cedar Wood)")
        zip_code = st.text_input("Job Zip Code")
        extra_notes = st.text_input("Extra Notes (Optional)")
        submit = st.form_submit_button("Generate Professional Estimate")

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
                st.session_state['data'] = completion.choices[0].message.parsed
                st.session_state['p_type'] = project_type
                st.session_state['dims'] = dimensions
                st.session_state['zip_c'] = zip_code
            except Exception as e:
                st.error(f"Error: {str(e)}")

    if 'data' in st.session_state:
        data = st.session_state['data']
        st.success("🎉 Estimate Complete!")
        st.subheader(f"💰 Grand Total: ${data.grand_total:.2f}")
        
        pdf_file = generate_pdf(data, st.session_state['p_type'], st.session_state['dims'], st.session_state['zip_c'])
