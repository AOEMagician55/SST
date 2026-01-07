import streamlit as st
import pandas as pd
from openai import OpenAI

# ---------------- Streamlit App Configuration ----------------
st.set_page_config(layout="centered", page_title="AI Career Suggestion App")
st.title("💼 AI-Powered Career Suggestion App")
st.subheader("Describe your skills, interests, and passions, and get suggested careers with how to get there!")

# ---------------- OpenAI Client ----------------
# Make sure your OpenAI API key is in secrets.toml: OPENAI_API_KEY
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("OpenAI API key not found. Please add it to your secrets.toml or Streamlit Cloud secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# ---------------- Streamlit Form ----------------
with st.form(key="career_form"):
    user_prompt = st.text_area(
        "Describe your skills, interests, or what you enjoy doing",
        height=200
    )
    submitted = st.form_submit_button("Get Career Suggestions")

# ---------------- Generate Career Suggestions ----------------
if submitted:
    st.info("Analyzing your input with AI...")

    # Build the prompt for GPT
    ai_prompt = f"""
You are a career advisor AI. 

User description: {user_prompt}

Task:
1. Suggest 3-5 careers that match the user's skills and interests.
2. For each career, provide a clear roadmap of how to get there in bullet points.
3. Respond in JSON format as a list of objects with fields "Career" and "How_to_get_there".
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful career advisor."},
                {"role": "user", "content": ai_prompt}
            ]
        )

        # Extract text
        text_response = response.choices[0].message.content

        # Try to parse JSON from AI output
        import json
        try:
            career_list = json.loads(text_response)
            df = pd.DataFrame(career_list)
        except:
            # Fallback if AI output is not valid JSON
            st.warning("Could not parse AI response as JSON. Showing raw response:")
            st.text(text_response)
        else:
            st.success("Here are your AI-generated career suggestions!")
            st.table(df)

    except Exception as e:
        st.error(f"Error generating career suggestions: {e}")
