import streamlit as st
import os
from openai import OpenAI
from pydantic import BaseModel
from typing import List
from pdf_builder import generate_pdf

# --- CLEAN ENTERPRISE CONFIGURATION ---
st.set_page_config(
    page_title="Quick Quote AI - Premium Console", 
    page_icon="🏗️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZE TRIAL VALUE HUD COUNTER ---
if 'quotes_used' not in st.session_state:
    st.session_state['quotes_used'] = 0

FREE_LIMIT = 5
remaining_quotes = FREE_LIMIT - st.session_state['quotes_used']

# --- SIDEBAR HUD DISPLAY WITH MULTI-TRADE PROFILE SELECTOR ---
st.sidebar.image("https://icons8.com", width=65)
st.sidebar.title("Quick Quote AI")
st.sidebar.markdown(f"**⚡ System Status:** `PRO BETA`")
st.sidebar.markdown(f"**📊 Usage Allocation:** `{remaining_quotes} / {FREE_LIMIT} Remaining`")
st.sidebar.markdown("---")

# 🧰 The Onboarding Trade Profiler Matrix Injection
user_trade = st.sidebar.selectbox(
    "Select Your Field Trade Profile:",
    ["🏗️ General Contractor", "🏠 Roofer / Siding Tech", "🪠 Professional Plumber", "⚡ Master Electrician", "🪵 Carpenter / Deck Builder"]
)
st.sidebar.success(f"Workspace optimized for: **{user_trade}**")
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
    st.title("🏗️ Stop Losing Construction Deals to Slow Estimates")
    st.subheader("Close residential clients directly from the driveway in under 30 seconds.")
    st.write("")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("### ⚡ 30-Second Quotes")
            st.write("Ditch evening paperwork. Type parameters right at the job site and let regional AI models construct cost itemizations instantly.")
    with col2:
        with st.container(border=True):
            st.markdown("### 🧾 Zero Speculation")
            st.write("Build massive customer trust. Hand your client a transparent material and labor breakdown that removes price haggling completely.")
    with col3:
        with st.container(border=True):
            st.markdown("### 📥 Instant PDF Delivery")
            st.write("Generate professional proposals instantly. Click one button to compile and text or email a polished quote before your competitors leave the job site.")
        
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
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.write(reply)
        except Exception as e:
            st.error(f"Bot Offline: {str(e)}")

# =========================================================
# MONITOR 2: GATED DYNAMIC ESTIMATION WORKSPACE
# =========================================================
elif page_selection == "🏗️ AI Estimate Engine":
    st.title("🏗️ Quick Quote AI Estimation Console")
    st.write(f"Input your raw parameters below. Your console has been dynamically tailored to: **{user_trade}**.")
    
    if st.session_state['quotes_used'] >= FREE_LIMIT:
        st.error("🚨 Free Beta Limit Reached!")
        st.warning("You have successfully generated your 5 free project estimates. To unlock unlimited calculations and custom PDF proposal downloads for your field crew, please activate a license under Premium Licensing.")
    else:
        # ⚡ DYNAMIC INPUT FORM HINTS LOGIC BASED ON SIDEBAR TRADE SELECTION ⚡
        with st.form("quote_form"):
            st.markdown(f"### 📋 Project Configuration Form — {user_trade}")
            
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
            extra_notes = st.text_input("Extra Client Demands or Site Access Notes (Optional)")
            submit = st.form_submit_button("Generate Professional Estimate Array")

        if submit:
            if not dimensions or not zip_code:
                st.error("Please fill out Size and Zip Code.")
            elif not os.environ.get("OPENAI_API_KEY"):
                st.error("API Key missing in cloud setup.")
            else:
                st.write("🔄 Calculating regional rates and compiling cost table...")
                try:
                    client = OpenAI()
                    system_prompt = f"You are an expert construction estimator specialized exclusively in the field of: {user_trade}. Output highly accurate, professional itemized cost estimates matching this trade's exact current market metrics."
                    user_prompt = f"Trade Context: {user_trade}\nMaterials/Specs: {materials_requested}\nScope/Dimensions: {dimensions}\nZip: {zip_code}\nNotes: {extra_notes}"
                    
                    completion = client.beta.chat.completions.parse(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                        response_format=AIQuoteResponse,
                    )
                    st.session_state['data'] = completion.choices[0].message.parsed
                    st.session_state['p_type'] = user_trade
                    st.session_state['dims'] = dimensions
                    st.session_state['zip_c'] = zip_code
                    
                    st.session_state['quotes_used'] += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    if 'data' in st.session_state:
        data = st.session_state['data']
        st.success("🎉 Estimate Complete!")
        
        with st.container(border=True):
            st.subheader(f"💰 Grand Total: ${data.grand_total:.2f}")
        st.write("")
        
        pdf_file = generate_pdf(data, st.session_state['p_type'], st.session_state['dims'], st.session_state['zip_c'])
        st.download_button(label="📥 Download Estimate Profile as PDF", data=pdf_file, file_name=f"Estimate_{st.session_state['p_type'].replace(' ', '_')}.pdf", mime="application/pdf")
        
        st.write(f"**Justification:** {data.business_justification}")
        st.write(f"**Days to Complete:** {data.estimated_days_to_complete} business days")
        
        st.markdown("### 🪵 Materials Itemization")
        for item in data.materials_list:
            st.write(f"• **{item.item_name}**: {item.quantity} {item.unit} @ ${item.estimated_cost_per_unit:.2f}/unit = **${item.total_item_cost:.2f}**")
            
        st.markdown("### 🛠️ Regional Labor Costs")
        for labor in data.labor_list: