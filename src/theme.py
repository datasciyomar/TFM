import os
import streamlit as st
import matplotlib.pyplot as plt

def apply_theme():
    """
    Inyecta dinámicamente un toggle para alternar modos Claro/Oscuro en la sesión,
    y carga el CSS y configuración de Matplotlib correspondientes.
    """
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    # Agregar el toggle en la barra lateral siempre que se renderice esto
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        # Usamos toggle
        mode = st.toggle("Modo Oscuro", value=st.session_state.dark_mode)
        if mode != st.session_state.dark_mode:
            st.session_state.dark_mode = mode
            st.rerun()

    # Determinar qué archivo CSS cargar
    css_file = "style_dark.css" if st.session_state.dark_mode else "style.css"
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", css_file)

    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Forzar a matplotlib a respetar el tema de Streamlit
    if st.session_state.dark_mode:
        plt.style.use("dark_background")
        # Ajustes adicionales para que matplotlib oscuro parezca premium y transparente
        plt.rcParams.update({
            "axes.facecolor": "none",
            "figure.facecolor": "none",
            "savefig.facecolor": "none",
            "text.color": "#f8fafc",
            "axes.labelcolor": "#cbd5e1",
            "xtick.color": "#94a3b8",
            "ytick.color": "#94a3b8",
            "axes.edgecolor": "#334155"
        })
    else:
        plt.style.use("default")
        plt.rcParams.update({
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "text.color": "#334155",
            "axes.labelcolor": "#475569",
            "xtick.color": "#64748b",
            "ytick.color": "#64748b",
            "axes.edgecolor": "#cbd5e1"
        })
