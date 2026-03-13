"""Simple password authentication for the dashboard."""

import streamlit as st


def check_password():
    """Returns True if the user has entered the correct password."""
    if st.session_state.get("authenticated"):
        return True

    # Centered login card
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; margin-top:15vh;">
            <h1 style="font-size:2.4rem; font-weight:700; margin-bottom:4px;">
                OOP Email Dashboard
            </h1>
            <p style="color:#888; font-size:1rem; margin-bottom:2rem;">
                Enter the team password to continue
            </p>
        </div>
        """, unsafe_allow_html=True)

        password = st.text_input("Password", type="password", key="password_input",
                                 label_visibility="collapsed", placeholder="Password")
        if st.button("Sign In", type="primary", use_container_width=True):
            if password == st.secrets["password"]:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password")

    return False
