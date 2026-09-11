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

# --- SIDEBAR HUD DISPLAY ---
st.sidebar.image("https://icons8.com", width=65)
st.sidebar.title("Quick Quote AI")
st.sidebar.markdown(f"**⚡ System Status:** `PRO BETA`")
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
                    st.session_state['data'] = completion.choices.message.parsed
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
            st.write(f"• **{labor.item_name}**: {labor.quantity} {labor.unit} @ ${labor.estimated_cost_per_unit:.2f}/unit = **${labor.total_item_cost:.2f}**")

# =========================================================
# MONITOR 3: SUBSCRIPTION BILLING HUD
# =========================================================
elif page_selection == "💳 Premium Licensing":
    st.title("💳 Secure Your Active Enterprise License")
    st.write("Unlock the absolute driveway sales weapon for your field operations crew.")
    st.markdown("---")
    
    tier1, tier2, tier3 = st.columns(3)
    
    with tier1:
        with st.container(border=True):
            st.markdown("### 🆕 Free Test Tier")
            st.markdown("## **$0.00 / mo**")
            st.write("• 5 Total Free Estimates")
            st.write("• Basic On-Screen Calculator")
            st.write("❌ No PDF Document Downloads")
            st.write("❌ No AI Client Lead Generator Bot")
            st.write("")
            st.button("Active Free Account", disabled=True, key="free_btn")
        
    with tier2:
        with st.container(border=True):
            st.markdown("### 🛠️ Standard License")
            st.markdown("## **$30.00 / mo**")
            st.write("• 25 Automated Estimates / Mo")
            st.write("• Uncapped Custom PDF Downloads")
            st.write("• Multi-Device Phone Access")
            st.write("❌ No AI Client Lead Generator Bot")
            st.write("")
            st.markdown("[🔥 Activate Standard Link](https://stripe.com)")
        
    with tier3:
        with st.container(border=True):
            st.markdown("### 👑 Unlimited Premium")
            st.markdown("## **$99.00 / mo**")
            st.write("• **Unlimited Estimates Forever**")
            st.write("• Uncapped Custom PDF Downloads")
            st.write("• Full AI Customer Support Lead Bot")
            st.write("• Lifetime Data Proof Storage Records")
            st.write("")
# =========================================================
# THE LIVE WEB-ROUTED FEEDBACK ENGINE (RE-ADDED & FIXED)
# =========================================================
st.markdown("---")
st.subheader("💡 Founder Beta Feedback")
st.write("Help me build the ultimate driveway tool for your business. Tell me what features you want next!")

# Explicitly import the requests library inside this module block
import requests

with st.form("feedback_form", clear_on_submit=True):
    contractor_name = st.text_input("Your Name / Company Name")
    feedback_text = st.text_area("What updates or features do you need? (e.g., custom logo uploader, past quote ledger, text alerts)")
    submit_feedback = st.form_submit_button("Submit Anonymous Note to Founder")

if submit_feedback:
    if not feedback_text:
        st.warning("Please enter your message before submitting.")
    else:
        # 🔗 PLACE YOUR COPIED FORMSPREE LINK EXACTLY INSIDE THESE QUOTES:
        FORMSPREE_URL = "https://formspree.io/f/xppzbyol"
        
        payload = {
            "Company": contractor_name,
            "Feedback": feedback_text
        }
        
        try:
            response = requests.post(FORMSPREE_URL, json=payload)
            if response.status_code == 200:
                st.success("🎉 Feedback submitted directly to the founder's email! Thank you.")
            else:
                st.error("Submission error. Please verify your Formspree Key or try again.")
        except Exception as e:
            st.error("Network connection offline. Please try again.")

