import streamlit as st
import os
from openai import OpenAI
from pydantic import BaseModel
from typing import List
from pdf_builder import generate_pdf

# --- ENTERPRISE CONFIGURATION ---
st.set_page_config(
    page_title="Quick Quote AI - Premium Console", 
    page_icon="🏗️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 🎨 THE ULTIMATE HIGH-VISIBILITY MIDNIGHT SLATE OVERRIDES ---
st.markdown("""
    <style>
        .stApp {
            background-color: #0b0f19 !important;
            color: #f3f4f6 !important;
        }
        h1, h2, h3, h4, p, label, .stMarkdown {
            color: #ffffff !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        }
        div[data-testid="stForm"] {
            background-color: #111827 !important;
            border: 1px solid #1f2937 !important;
            border-radius: 8px !important;
            padding: 2rem !important;
        }
        div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
            background-color: #1f2937 !important;
            color: #ffffff !important;
            border: 1px solid #4b5563 !important;
            border-radius: 6px !important;
        }
        button, .stButton button, div[data-testid="stForm"] button {
            background-color: #1f2937 !important;
            color: #ffffff !important;
            border: 2px solid #6366f1 !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            padding: 0.5rem 1.5rem !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        button:hover, .stButton button:hover {
            background-color: #2563eb !important;
            border-color: #3b82f6 !important;
            color: #ffffff !important;
        }
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE CORE LOCAL VOLATILE STORAGE ---
if 'quotes_history' not in st.session_state:
    st.session_state['quotes_history'] = []
if 'base_labor_rate' not in st.session_state:
    st.session_state['base_labor_rate'] = 85.0
if 'company_markup' not in st.session_state:
    st.session_state['company_markup'] = 20.0
if 'uploaded_logo' not in st.session_state:
    st.session_state['uploaded_logo'] = None
if 'company_name' not in st.session_state:
    st.session_state['company_name'] = ""

# =========================================================
# MONITOR 1: THE OPEN SIDEBAR CONSOLE CONTROLS
# =========================================================
st.sidebar.title("Quick Quote AI")
st.sidebar.markdown(f"**System Status:** `ACTIVE PUBLIC CONSOLE`")
st.sidebar.markdown("---")

user_trade = st.sidebar.selectbox(
    "Select Field Trade Profile:",
    ["General Contractor", "Roofer / Siding Tech", "Professional Plumber", "Master Electrician", "Carpenter / Deck Builder"]
)
st.sidebar.success(f"Console Calibrated to: {user_trade}")
st.sidebar.markdown("---")

# Display thumbnail preview of corporate logo if uploaded inside the sidebar layout
if st.session_state['uploaded_logo'] is not None:
    st.sidebar.markdown("### Active Workspace Identity")
    if st.session_state['company_name']:
        st.sidebar.markdown(f"**Firm Name:** `{st.session_state['company_name']}`")
    st.sidebar.image(st.session_state['uploaded_logo'], width=120)
    st.sidebar.markdown("---")

page_selection = st.sidebar.radio("Navigate Dashboard Workspace", ["AI Estimate Engine", "Workspace Profiler & Ledger", "Premium Licensing"])

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

# =========================================================
# MONITOR 2: THE CALCULATION SYSTEM MODULES
# =========================================================
if page_selection == "AI Estimate Engine":
    st.title("Quick Quote AI Estimation Console")
    st.write(f"Input your raw parameters below to calculate instantaneous itemizations calibrated to: {user_trade}.")
    
    with st.form("quote_form"):
        st.markdown(f"### Project Configuration Form — {user_trade}")
        
        dim_hint = "Project Parameters / Sizing Data"
        mat_hint = "Paste your raw text layout parameters, labor tasks, or material counts here"
        
        if "Roofer" in user_trade:
            dim_hint = "Project Size / Scope (e.g., 25 Squares, 2500 sq ft, 8/12 Pitch Angle)"
            mat_hint = "Required Materials & Specifications (e.g., Timberline HDZ Shingles, Synthetic Underlayment, Ice & Water Shield)"
        elif "Plumber" in user_trade:
            dim_hint = "Project Size / Scope (e.g., 3-Bathroom Rough-In, 40 Linear Feet of Trenching)"
            mat_hint = "Required Materials & Specifications (e.g., Schedule 40 PVC, Copper PEX Piping, Fixture counts and brands)"
        elif "Electrician" in user_trade:
            dim_hint = "Project Size / Scope (e.g., 200 Amp Service Upgrade, 2500 sq ft House Rewire)"
            mat_hint = "Required Materials & Specifications (e.g., Romex 14/2 Wire, Siemens Panel Board, Outlet/Switch counts)"
        elif "Carpenter" in user_trade:
            dim_hint = "Project Size / Scope (e.g., 16x20 Floating Deck, 80 Linear Feet of Privacy Fencing)"
            mat_hint = "Required Materials & Specifications (e.g., Pressure Treated Premium Lumber, Composite Decking boards)"

        dimensions = st.text_input(dim_hint)
        materials_requested = st.text_area(mat_hint, height=120)
        zip_code = st.text_input("Job Zip Code / Region")
        extra_notes = st.text_input("Extra Notes and Access Demands (Optional)")
        submit = st.form_submit_button("Generate Professional Estimate Array")

    if submit:
        if not dimensions or not zip_code:
            st.error("Please fill out Size and Zip Code.")
        elif not os.environ.get("OPENAI_API_KEY"):
            st.error("System Matrix Configuration Warning: API Key missing.")
        else:
            st.write("🔄 Activating Real-Time Price Indexing and calculating regional rates...")
            client = OpenAI()
            system_prompt = (
                f"You are an expert construction estimator specialized exclusively in the field of: {user_trade}. "
                f"The current year is 2026. Calculate material costs based on wholesale prices. "
                f"Incorporate an operational baseline calculation assuming a standard crew labor cost index of ${st.session_state['base_labor_rate']}/hr "
                f"and factor in an overall company structural project profit markup margin profile parameter of {st.session_state['company_markup']}%. "
                f"Calibrate all line items to match localized market rates for zip code {zip_code}. Output highly accurate industry-standard itemized matrices."
            )
            user_prompt = f"Trade Context: {user_trade}\nMaterials/Specs: {materials_requested}\nScope/Dimensions: {dimensions}\nZip / Geographic Region: {zip_code}\nNotes: {extra_notes}"
            
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                response_format=AIQuoteResponse,
            )
            parsed_response = completion.choices.message.parsed
            st.session_state['data'] = parsed_response
            st.session_state['p_type'] = user_trade
            st.session_state['dims'] = dimensions
            st.session_state['zip_c'] = zip_code
            
            st.session_state['quotes_history'].append({
                "Trade": user_trade,
                "Scope": dimensions,
                "Zip": zip_code,
                "Total": parsed_response.grand_total
            })
            st.rerun()

    if 'data' in st.session_state:
        data = st.session_state['data']
        st.success("Estimate Complete and Appended to Local Session Workspace!")
        
        with st.container(border=True):
            st.subheader(f"Grand Total: ${data.grand_total:.2f}")
        st.write("")
        
        pdf_file = generate_pdf(
            data, 
            st.session_state['p_type'], 
            st.session_state['dims'], 
            st.session_state['zip_c'],
            logo_image=st.session_state['uploaded_logo'],
            firm_name=st.session_state['company_name']
        )
        st.download_button(label="Download Estimate Profile as PDF", data=pdf_file, file_name=f"Estimate_{st.session_state['p_type'].replace(' ', '_')}.pdf", mime="application/pdf")
        
        st.write(f"**Justification:** {data.business_justification}")
        st.write(f"**Days to Complete:** {data.estimated_days_to_complete} business days")
        
        st.markdown("### Materials Itemization")
        mat_table = [{"Item Name": m.item_name, "Qty": m.quantity, "Unit": m.unit, "Cost/Unit": f"${m.estimated_cost_per_unit:.2f}", "Total": f"${m.total_item_cost:.2f}"} for m in data.materials_list]
        st.dataframe(mat_table, use_container_width=True)
            
        st.markdown("### Regional Labor Costs")
        lab_table = [{"Operation": l.item_name, "Hours/Qty": l.quantity, "Unit": l.unit, "Rate/Unit": f"${l.estimated_cost_per_unit:.2f}", "Total": f"${l.total_item_cost:.2f}"} for l in data.labor_list]
        st.dataframe(lab_table, use_container_width=True)

# =========================================================
# MONITOR 3: THE ADVANCED INDIVIDUAL SPECIFICATION PROFILER
# =========================================================
