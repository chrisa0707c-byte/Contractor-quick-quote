import streamlit as st
import os
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

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

# --- STEP 2: The Visual Input Form ---
with st.form("quote_form"):
    project_type = st.selectbox("Project Type", ["Roofing", "Painting", "Plumbing", "Drywall", "Flooring", "Deck Construction", "General Handyman"])
    dimensions = st.text_input("Project Size / Scope (e.g., 500 sq ft)")
    materials_requested = st.text_input("Materials Preferred (e.g., Premium Cedar Wood)")
    zip_code = st.text_input("Job Zip Code")
    extra_notes = st.text_input("Extra Notes (Optional)")
    
    submit = st.form_submit_button("Generate Professional Estimate")

# --- STEP 3: Handle AI Processing ---
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
            data = completion.choices[0].message.parsed
            
            st.success("🎉 Estimate Complete!")
            st.subheader(f"💰 Grand Total: ${data.grand_total:.2f}")
            st.write(f"**Justification:** {data.business_justification}")
            st.write(f"**Days to Complete:** {data.estimated_days_to_complete} business days")
            
            st.markdown("### 🪵 Materials Itemization")
            for item in data.materials_list:
                st.write(f"• **{item.item_name}**: {item.quantity} {item.unit} @ ${item.estimated_cost_per_unit:.2f}/unit = **${item.total_item_cost:.2f}**")
                
            st.markdown("### 🛠️ Regional Labor Costs")
            for labor in data.labor_list:
                st.write(f"• **{labor.item_name}**: {labor.quantity} {labor.unit} @ ${labor.estimated_cost_per_unit:.2f}/unit = **${labor.total_item_cost:.2f}**")

        except Exception as e:
            st.error(f"Error: {str(e)}")

# --- STEP 4: The Passive Feedback Box ---
st.markdown("---")
st.subheader("💡 Founder Beta Feedback")
st.write("Help me build the ultimate tool for your business. Tell me what features you want next!")

with st.form("feedback_form", clear_on_submit=True):
    contractor_name = st.text_input("Your Name / Company")
    feedback_text = st.text_area("What features or updates do you need? (e.g., Download PDF button, custom logo uploader)")
    submit_feedback = st.form_submit_button("Submit Anonymous Feedback")

if submit_feedback:
    if not feedback_text:
        st.warning("Please type your feedback before submitting.")
    else:
        # Appends the feedback instantly to a clean text file on your cloud server
        with open("user_feedback.txt", "a") as f:
            f.write(f"Company: {contractor_name} | Feedback: {feedback_text}\n")
        st.success("🔥 Feedback submitted directly to the founder! Thank you.")
