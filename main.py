from openai import OpenAI
import streamlit as st
import pandas as pd

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if submitted:
    st.info("Analyzing your input with AI...")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a career advisor. "
                    "Return ONLY valid JSON with this structure:\n"
                    "Give tips on where to go from post secondary school"
                    "{\n"
                    '  "careers": [\n'
                    '    {"Career": "...", "How_to_get_there": ["step 1", "step 2"]}\n'
                    "  ]\n"
                    "}"
                ),
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    data = response.choices[0].message.content
    import json
    parsed = json.loads(data)

    df = pd.DataFrame(parsed["careers"])
    st.success("Career suggestions generated!")
    st.table(df)

