import os

import streamlit as st
import requests

api_base_url = os.getenv(
    "API_BASE_URL",
    "http://localhost:8000"
).rstrip("/")

st.title(
    "AI Incident Resolution Platform"
)

incident_id = st.text_input(
    "Incident ID"
)

title = st.text_input(
    "Title"
)

description = st.text_area(
    "Incident Description"
)

if st.button(
        "Analyze Incident"):

    payload = {

        "incident_id":
            incident_id,

        "title":
            title,

        "description":
            description
    }

    response = requests.post(
        f"{api_base_url}/incident",
        json=payload
    )

    st.json(
        response.json()
    )