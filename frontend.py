import streamlit as st
import os
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

# Set up the visual page title
st.title("🏗️ Contractor AI Quick-Quote")
st.write("Generate client-ready estimates in 30 seconds.")

# --- STEP 1: Define the strict data structure for OpenAI ---
class LineItem(BaseModel):
    item_name: str = Field(..., description="Name of the material or labor task")
    quantity: float
    unit: str = Field(..., description="e.g., sq ft, hours, bags")
    estimated_cost_per_unit: float
    total_item_cost: float

class AIQuoteResponse(BaseModel):
    business_justification: str = Field(..., description="Summary of pricing logic based on location/materials.")
    estimated_days_to_complete: int
    materials_list: List[LineItem]
    labor_list: List[LineItem]
    grand_total: float

# --- STEP 2: Build the Visual Form ---
with st.form("quote_form"):
    project_type = st.selectbox("Project Type", ["Roofing", "Painting", "Plumbing", "Drywall", "Flooring", "Deck Construction", "General Handyman"])
    dimensions = st.text_input("Project Size / Scope (e.g., 500 sq ft)")
    materials_requested = st.text_input("Materials Preferred (e.g., Cedar Wood)")
    zip_code = st.text_input("Job Zip Code")
    extra_notes = st.text_input("Extra Notes (Optional)")
    
    submit = st.form_submit_button("Generate Professional Estimate")

# --- STEP 3: Handle the AI Processing directly inside this file ---
if submit:
    if not dimensions or not zip_code:
        st.error("Please fill out Size and Zip Code.")
    elif not os.environ.get("OPENAI_API_KEY"):
        st.error("API Key not found. Please set your OPENAI_API_KEY in the terminal.")
    else:
        st.write("🔄 Calculating costs with AI... please wait...")
        
        try:
            # Connect directly to OpenAI using your secret key from the terminal
            client = OpenAI()
            
            system_prompt = (
                "You are an expert construction estimator. Your job is to output a professional, "
                "accurate, itemized cost estimate for a contractor to present to a client. "
                "Calculate market rates for materials and regional labor costs based on the provided data."
            )
            
            user_prompt = (
                f"Project Type: {project_type}\n"
                f"Materials: {materials_requested if materials_requested else 'Standard contractor grade'}\n"
                f"Dimensions/Scope: {dimensions}\n"
                f"Location (Zip Code): {zip_code}\n"
                f"Additional Details: {extra_notes if extra_notes else 'None'}"
            )

            # Call the AI model using Structured Outputs
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=AIQuoteResponse,
            )
            
            # Pull the data (Notice the [0] is added here perfectly!)
            data = completion.choices[0].message.parsed
            
            # --- STEP 4: Render the Beautiful Output Tables ---
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
            st.error(f"AI Processing Error: {str(e)}")
