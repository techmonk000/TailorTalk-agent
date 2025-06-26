import streamlit as st
import requests

st.set_page_config(page_title="TailorTalk Agent", page_icon="🧠")

st.title("🧵 TailorTalk Chatbot")
st.markdown("_Book your meeting naturally!_")

if "chat" not in st.session_state:
    st.session_state.chat = []

user_input = st.chat_input("Say something...")
if user_input:
    st.session_state.chat.append(("user", user_input))
    with st.spinner("Thinking..."):
        res = requests.post("http://localhost:8000/chat", json={"message": user_input})
        bot_reply = res.json()["response"]
        st.session_state.chat.append(("bot", bot_reply))

for role, msg in st.session_state.chat:
    if role == "user":
        st.chat_message("user").markdown(msg)
    else:
        st.chat_message("assistant").markdown(msg)
