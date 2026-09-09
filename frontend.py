import streamlit as st
import os
from openai import OpenAI
from pydantic import BaseModel
from typing import List
from pdf_builder import generate_pdf

# --- THE NATIVE PREMIUM AESTHETIC THEME ENGINE ---
st.set_page_config(
    page_title="Quick Quote AI - Premium Console", 
    page_icon="🏗️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Raw CSS injection to create an elite, modernist software dashboard design
st.markdown("""
    <style>
        /* Modernist Radial Background Matrix */
        .stApp {
            background: radial-gradient(circle, #0A192F 0%, #020C1B 100%) !important;
            color: #F4F6F9 !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        
        /* Sidebar Polish */
        section[data-testid="stSidebar"] {
            background-color: #020C1B !important;
            border-right: 1px solid #1E293B;
        }
        
        /* Floating Glassmorphic Container Cards */
        div[data-testid="stForm"], .stAlert, div.element-container div.stMarkdown div {
            background: rgba(13, 27, 42, 0.65) !important;
            border: 1px solid #FF6B35 !important;
            border-radius: 12px !important;
            padding: 25px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
        }
        
        /* Neon Button Styling Rules */
        div.stButton > button:first-child {
            background: linear-gradient(135deg, #FF6B35 0%, #D9534F 100%) !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4) !important;
        }
        div.stButton > button:first-child:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(255, 107, 53, 0.6) !important;
        }
        
        /* Polished Form Inputs */
        input, select, textarea {
            background-color: #020C1B !important;
            color: white !important;
            border: 1px solid #1E293B !important;
            border-radius: 6px !important;
        }
        input:focus {
            border-color: #FF6B35 !important;
            box-shadow: 0 0 10px rgba(255, 107, 53, 0.5) !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE TRIAL VALUE HUD COUNTER ---
if 'quotes_used' not in st.session_state:
    st.session_state['quotes_used'] = 0

FREE_LIMIT = 5
remaining_quotes = FREE_LIMIT - st.session_state['quotes_used']

# --- SIDEBAR HUD DISPLAY ---
st.sidebar.image("https://icons8.com", width=65)
st.sidebar.title("Quick Quote AI")
st.sidebar.markdown(f"**⚡ System Status:** <span style='color:#FF6B35;font-weight:bold;'>PRO BETA</span>", unsafe_allow_html=True)
st.sidebar.markdown(f"**📊 Usage Allocation:** `{remaining_quotes} / {FREE_LIMIT} Remaining`")
st.sidebar.markdown("---")

page_selection = st.sidebar.radio("Navigate Enterprise Console", ["🏠 Platform Overview", "🏗️ AI Estimate Engine", "💳 Premium Licensing"])

# --- DATA MODEL HOOKS ---
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
# MONITOR 1: BRAND SALES LANDING SUMMARY
# =========================================================
if page_selection == "🏠 Platform Overview":
    st.markdown("<h1 style='text-align: center; color: white;'>🏗️ Stop Losing Construction Deals to Slow Estimates</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #FF6B35;'>Close residential clients directly from the driveway in under 30 seconds.</h3>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div style='background:rgba(13,27,42,0.4);border-left:4px solid #FF6B35;padding:20px;border-radius:8px;'><h3>⚡ 30-Second Quotes</h3><p>Ditch evening paperwork. Type parameters right at the job site and let regional AI models construct cost itemizations instantly.</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div style='background:rgba(13,27,42,0.4);border-left:4px solid #FF6B35;padding:20px;border-radius:8px;'><h3>🧾 Zero Speculation</h3><p>Build massive customer trust. Hand your client a transparent material and labor breakdown that removes price haggling completely.</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div style='background:rgba(13,27,42,0.4);border-left:4px solid #FF6B35;padding:20px;border-radius:8px;'><h3>📥 Instant PDF Delivery</h3><p>Generate professional proposals instantly. Click one button to compile and text or email a polished quote before your competitors leave the job site.</p></div>", unsafe_allow_html=True)
        
    st.markdown("---")
    
    # THE CLIENT INQUIRY SUPPORT BOT PANEL
    st.subheader("🤖 Client Lead Generator Bot (Beta Preview)")
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

# =========================================================
# MONITOR 2: GATED ESTIMATION WORKSPACE
# =========================================================
elif page_selection == "🏗️ AI Estimate Engine":
    st.title("🏗️ Quick Quote AI Estimation Console")
    st.write("Input project parameters below to deploy instant material and labor data arrays.")
    
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
                        response_format=AIQuoteResponse,
                    )
                    st.session_state['data'] = completion.choices[0].message.parsed
                    st.session_state['p_type'] = project_type
                    st.session_state['dims'] = dimensions
                    st.session_state['zip_c'] = zip_code
                    
                    st.session_state['quotes_used'] += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    if 'data' in st.session_state:
        data = st.session_state['data']
        st.success("🎉 Estimate Complete!")
        
        # Floating styled output metrics dashboard