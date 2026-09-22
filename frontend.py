import streamlit as st
import os
from openai import OpenAI
from pydantic import BaseModel
from typing import List
from pdf_builder import generate_pdf
from supabase import create_client, Client

# --- ENTERPRISE CONFIGURATION ---
st.set_page_config(
    page_title="Quick Quote AI - Premium Console", 
    page_icon="🏗️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 🎨 THE ULTIMATE MIDNIGHT DARK-MODE SKIN OVERRIDES ---
# Injecting direct CSS rules to style inputs, cards, and enforce a clean charcoal corporate aesthetic
st.markdown("""
    <style>
        /* Force the core application background to a deep midnight charcoal slate */
        .stApp {
            background-color: #0b0f19 !important;
            color: #f3f4f6 !important;
        }
        
        /* Enforce crisp white high-visibility text on all standard headers */
        h1, h2, h3, h4, p, label, .stMarkdown {
            color: #ffffff !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        }
        
        /* Style form container cards into glowing enterprise modules */
        div[data-testid="stForm"] {
            background-color: #111827 !important;
            border: 1px solid #1f2937 !important;
            border-radius: 8px !important;
            padding: 2rem !important;
        }
        
        /* Style internal text inputs to match the dark theme canvas */
        div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
            background-color: #1f2937 !important;
            color: #ffffff !important;
            border: 1px solid #374151 !important;
            border-radius: 6px !important;
        }
        
        /* Remove standard Streamlit footer visual branding branding rows */
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- SECURE SUPABASE CLOUD DATABASE WIRES ---
SUPABASE_URL = "https://supabase.co"
SUPABASE_KEY = "sb_publishable_sJKogzgeJtD296ygXWd3rPExC2NlZTMzNmE0Y2M0YmFiNGM0NmY0YTllMDkyNDU1N2U3YTMxYzE4OGJhNGE5NDRlOGQyNTllNjc3ZDcyODRiZg=="

@st.cache_resource
def init_supabase():
    if SUPABASE_URL and SUPABASE_KEY:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    return None

supabase: Client = init_supabase()

# --- INITIALIZE CORE SECURITY STATES ---
if "quotes_used" not in st.session_state:
    st.session_state["quotes_used"] = 0

FREE_LIMIT = 5
remaining_quotes = FREE_LIMIT - st.session_state["quotes_used"]

# =========================================================
# MONITOR 0: NATIVE STREAMLIT AUTHENTICATION PORTAL GATEWAY
# =========================================================
# Using official native auth routing rules to completely avoid manual URL endpoint pathing
if not st.experimental_user.is_logged_in:
    st.title("Quick Quote AI")
    st.subheader("Enterprise Workspace Access Portal")
    st.write("Secure multi-tenant workspace console. Authenticate your trade credentials to enter.")
    st.markdown("---")
    st.info("Please click the controller below to securely log into your secure contractor vault.")
    
    # Renders an un-hackable, secure official login button linked straight to your secrets ecosystem
    st.login()
    st.stop()

# Capture the authenticated user's email cleanly from the secure environment layer
current_user_email = st.experimental_user.get("email", "beta.contractor@quickquote.ai")

# =========================================================
# MONITOR 1: THE ACTIVE AUTHORIZED WORKSPACE
# =========================================================
st.sidebar.title("Quick Quote AI")
st.sidebar.markdown(f"**Account:** `{current_user_email}`")
st.sidebar.markdown(f"**System Status:** `PRO BETA`")
st.sidebar.markdown(f"**Usage Allocation:** `{remaining_quotes} / {FREE_LIMIT} Remaining`")
st.sidebar.markdown("---")

user_trade = st.sidebar.selectbox(
    "Select Your Field Trade Profile:",
    ["General Contractor", "Roofer / Siding Tech", "Professional Plumber", "Master Electrician", "Carpenter / Deck Builder"]
)
st.sidebar.success(f"Workspace optimized for: {user_trade}")
st.sidebar.markdown("---")

page_selection = st.sidebar.radio("Navigate Enterprise Console", ["Platform Overview", "AI Estimate Engine", "Premium Licensing"])

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Securely Log Out of Console"):
    st.logout()
    st.rerun()

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

if page_selection == "Platform Overview":
    st.title("Stop Losing Construction Deals to Slow Estimates")
    st.subheader("Close residential clients directly from the driveway in under 30 seconds.")
    st.write("")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("### 30-Second Quotes")
            st.write("Ditch evening paperwork. Type parameters right at the job site and let regional AI models construct cost itemizations instantly.")
    with col2:
        with st.container(border=True):
            st.markdown("### Zero Speculation")
            st.write("Build massive customer trust. Hand your client a transparent material and labor breakdown that removes price haggling completely.")
    with col3:
        with st.container(border=True):
            st.markdown("### Instant PDF Delivery")
            st.write("Generate professional proposals instantly. Click one button to compile and text or email a polished quote before your competitors leave the job site.")
        
    st.markdown("---")
    
    st.subheader("Client Lead Generator Bot (Beta Preview)")
    st.write("Embed this bot directly on your website to catch project details while you sleep.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your automated project assistant. Describe what trade work you need done, and I will capture the project scope."}]
        
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
                messages=[{"role": "system", "content": "You are a customer assistant for a top contracting firm. Guide them smoothly to capture scope data."}, *st.session_state.messages]
            )
            reply = response.choices.message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.write(reply)
        except Exception as e:
            st.error(f"Bot Offline: {str(e)}")

elif page_selection == "AI Estimate Engine":
    st.title("Quick Quote AI Estimation Console")
    st.write(f"Input your raw parameters below. Your console has been dynamically tailored to: {user_trade}.")
    
    if st.session_state['quotes_used'] >= FREE_LIMIT:
        st.error("Free Beta Limit Reached!")
        st.warning("You have successfully generated your 5 free project estimates. To unlock unlimited calculations and custom PDF proposal downloads for your field crew, please activate a license under Premium Licensing.")
    else:
        with st.form("quote_form"):
            st.markdown(f"### Project Configuration Form — {user_trade}")
            
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
            else:
                dim_hint = "Project Size / Scope (e.g., 500 sq ft Driveway, 1200 sq ft Full Basement Renovation)"
                mat_hint = "Required Materials & Specifications (Paste your raw text layout parameters, labor tasks, or material counts here)"

            dimensions = st.text_input(dim_hint)
            materials_requested = st.text_area(mat_hint, height=120)
            zip_code = st.text_input("Job Zip Code / Region")
            extra_notes = st.text_input("Extra Notes and Access Demands (Optional)")
            submit = st.form_submit_button("Generate Professional Estimate Array")

        if submit:
            if not dimensions or not zip_code:
                st.error("Please fill out Size and Zip Code.")
            elif not os.environ.get("OPENAI_API_KEY"):
