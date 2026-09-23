import streamlit as st
import os
from openai import OpenAI
from pydantic import BaseModel
from typing import List
from pdf_builder import generate_pdf
import requests

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

# --- SECURE AUTOMATED PROGRAMMATIC BACKEND BRIDGE WIRES ---
SUPABASE_URL = "https://supabase.co"
SUPABASE_KEY = "sb_publishable_sJKogzgeJtD296ygXWd3rPExC2NlZTMzNmE0Y2M0YmFiNGM0NmY0YTllMDkyNDU1N2U3YTMxYzE4OGJhNGE5NDRlOGQyNTllNjc3ZDcyODRiZg=="

# --- INITIALIZE CORE SECURITY AND ACCOUNT STATES ---
if "user_authenticated" not in st.session_state:
    st.session_state["user_authenticated"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if 'quotes_used' not in st.session_state:
    st.session_state['quotes_used'] = 0

FREE_LIMIT = 5
remaining_quotes = FREE_LIMIT - st.session_state['quotes_used']

# =========================================================
# MONITOR 0: THE ENTERPRISE GATEWAY (LOG IN / SIGN UP)
# =========================================================
if not st.session_state["user_authenticated"]:
    st.title("Quick Quote AI - Enterprise Access Portal")
    st.write("Secure multi-tenant workspace console. Authenticate your trade credentials to enter.")
    st.markdown("---")
    
    auth_mode = st.radio("Select Portal Action", ["Sign In to Account", "Create New Workspace (Sign Up)"])
    
    with st.form("auth_form", clear_on_submit=False):
        email = st.text_input("Corporate Email Address")
        password = st.text_input("Secure Vault Password", type="password")
        submit_auth = st.form_submit_button("Authenticate Credentials")
        
    if submit_auth:
        if not email or not password:
            st.error("Authentication Error: All fields are required.")
        else:
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            payload = {"email": email, "password": password}
            
            if auth_mode == "Create New Workspace (Sign Up)":
                # Explicit routing to your personal project endpoint tunnel
                endpoint = f"{SUPABASE_URL}/auth/v1/signup"
                try:
                    response = requests.post(endpoint, headers=headers, json=payload)
                    res_data = response.json()
                    if response.status_code == 200 or response.status_code == 201:
                        st.success("🎉 Workspace Registered! Please check your email inbox to confirm your verification link, then toggle to Sign In.")
                    else:
                        st.error(f"Registration Failed: {res_data.get('msg', res_data.get('error_description', 'Invalid Request'))}")
                except Exception as e:
                    st.error(f"Network Error: {str(e)}")
            else:
                # Explicit routing to your personal project token generation portal
                endpoint = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
                try:
                    response = requests.post(endpoint, headers=headers, json=payload)
                    res_data = response.json()
                    if response.status_code == 200:
                        st.session_state["user_authenticated"] = True
                        st.session_state["user_email"] = res_data["user"]["email"]
                        st.success("Access Granted. Initializing console...")
                        st.rerun()
                    else:
                        st.error(f"Access Denied: {res_data.get('error_description', res_data.get('msg', 'Invalid credentials'))}")
                except Exception as e:
                    st.error(f"Authentication Bridge Failed: {str(e)}")
    st.stop()

# =========================================================
# MONITOR 1: THE ACTIVE AUTHORIZED WORKSPACE
# =========================================================
st.sidebar.title("Quick Quote AI")
st.sidebar.markdown(f"**Account:** `{st.session_state['user_email']}`")
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
    st.session_state["user_authenticated"] = False
    st.session_state["user_email"] = None
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
