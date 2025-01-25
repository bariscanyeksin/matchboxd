import streamlit as st

def Navbar():
    with st.sidebar:
        st.page_link('app.py', label='Matchboxd', icon='🔥')
        st.page_link('pages/scout.py', label='Matchboxd-Scout', icon='🔍')
