import streamlit as st
import os
from openai import OpenAI
from pydantic import BaseModel
from typing import List
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- FORCE WORLD-CLASS DARK THEME INJECTOR ---
st.set_page_config(
    page_title="Quick Quote AI - Enterprise", 
    page_icon="🏗️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling rules
st.markdown("""
    <style>
        .reportview-container { background: #0A192F; color: #F4F6F9; }
        .sidebar .sidebar-content { background: #020C1B; }
        div.stButton > button:first-child {
            background-color: #FF6B35; color: white; border-radius: 6px;
            border: none; font-weight: bold; width: 100%; height: 3em;
        }
        div.stButton > button:first-child:hover { background-color: #FF8552; }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE USER ESTIMATE TRACKER (THE FREEMIUM COUNTER) ---
if 'quotes_used' not in st.session_state:
    st.session_state['quotes_used'] = 0

FREE_LIMIT = 5
remaining_quotes = FREE_LIMIT - st.session_state['quotes_used']

# --- SIDEBAR NAVIGATION CONTROL ---
st.sidebar.image("https://icons8.com", width=70)
st.sidebar.title("Quick Quote AI")
st.sidebar.markdown(f"**⚡ Account Status:** `Free Beta Tier`")
st.sidebar.markdown(f"**📊 Estimates Remaining:** `{remaining_quotes} / {FREE_LIMIT}`")
st.sidebar.markdown("---")

page_selection = st.sidebar.radio("Enterprise Console", ["🏠 Dashboard Home", "🏗️ AI Estimate Engine", "💳 Premium Licensing"])

# --- PDF GENERATOR CORE LOGIC ---
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
    t_mat = Table(mat_data, colWidths=[200, 50, 50, 80, 80])
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
    t_lab = Table(lab_data, colWidths=[200, 50, 50, 80, 80])
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
# PAGE 1: RE-ENGINEERED CORPORATE HOME OVERVIEW
# =========================================================
if page_selection == "🏠 Company Overview" or page_selection == "🏠 Company Overview":
    st.title("🏗️ Stop Losing Construction Deals to Slow Estimates")
    st.markdown("### Close residential clients directly from the driveway in under 30 seconds.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### ⚡ 30-Second Quotes\nDitch evening spreadsheet paperwork. Type parameters at the job site and let regional AI models construct cost itemizations instantly.")
    with col2:
        st.info("### 🧾 Zero Speculation\nBuild massive customer trust. Hand your client a transparent material and labor breakdown that removes price haggling completely.")
    with col3:
        st.info("### 📥 Instant PDF Delivery\nGenerate professional proposals instantly. Click one button to compile and text or email a polished quote before your competitors leave the job site.")
        
    st.markdown("---")
    
    # INTERACTIVE LEAD BOT PREVIEW
    st.subheader("🤖 Client Lead Generator Bot (Beta Preview)")
    st.write("Embed this bot directly on your website to catch project details while you sleep.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your project assistant. Describe what construction or trade work you need done, and I will capture the scope for the manager."}]
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if bot_input := st.chat_input("Type your construction inquiry here..."):
        st.session_state.messages.append({"role": "user", "content": bot_input})
        with st.chat_message("user"):
            st.write(bot_input)
            
        try:
            client = OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are a customer assistant for a top contracting firm. Guide them to provide scope or a zip code safely."}, *st.session_state.messages]
            )
            reply = response.choices.message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.write(reply)
        except Exception as e:
            st.error(f"Bot Offline: {str(e)}")

# =========================================================
# PAGE 2: FREE RE-GATED AI CALCULATION MACHINE
# =========================================================
elif page_selection == "🏗️ AI Estimate Engine":
    st.title("🏗️ Quick Quote AI Estimation Console")
    
    # HARD GATED CHECKPAYWALL LIMIT LOCK
    if st.session_state['quotes_used'] >= FREE_LIMIT:
        st.error("🚨 Free Beta Limit Reached!")
        st.warning("You have successfully generated your 5 free project estimates. To unlock unlimited calculations and custom PDF proposal downloads for your field crew, please activate a license under Premium Licensing.")
    else:
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
