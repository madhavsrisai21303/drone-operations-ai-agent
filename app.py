import streamlit as st
from agent import handle_message
from utils import load_data

st.set_page_config(page_title="Drone Operations AI", layout="wide")

st.title("🚁 Drone Operations Coordinator AI Agent")

st.write("Type commands like:")
st.write("- Assign mission M1")
st.write("- Show available pilots")
st.write("- Update Arjun to On Leave")
st.write("- Show maintenance drones")

# Load live data from Google Sheets
pilots, drones, missions = load_data()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("💬 Enter your message")

if st.button("Send"):
    response, pilots, drones, missions = handle_message(
        user_input, pilots, drones, missions
    )

    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("Agent", response))

for sender, msg in st.session_state.chat_history:
    st.write(f"**{sender}:** {msg}")
