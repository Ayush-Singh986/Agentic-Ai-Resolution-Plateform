import streamlit as st
import requests

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

        "http://localhost:8000/incident",

        json=payload
    )

    st.json(
        response.json()
    )