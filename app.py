import streamlit as st
import psycopg2
import datetime

# Panggil modul tampilan
from views.portal import render_portal
from views.form_kap1 import render_kap1
from views.form_kap2 import render_kap2
from views.dashboard_bbm import render_dashboard

st.set_page_config(page_title="Sistem Monitoring BBM PT ADM", layout="wide")

# Inisialisasi Session State
if 'selected_menu' not in st.session_state:
    st.session_state.selected_menu = "Portal Utama"

@st.cache_resource
def init_connection():
    try:
        db_url = st.secrets["SUPABASE_URL"]
        return psycopg2.connect(db_url)
    except Exception as e:
        st.error(f"Gagal terhubung ke database: {e}")
        return None

conn = init_connection()

# Sidebar Navigasi Utama
menu_options = ["Portal Utama", "Form Input KAP 1", "Form Input KAP 2", "Dashboard Monitoring"]
menu = st.sidebar.selectbox("Navigasi Menu", menu_options, index=menu_options.index(st.session_state.selected_menu))
st.session_state.selected_menu = menu

area_aktif = "Portal"
if menu == "Form Input KAP 1":
    area_aktif = "Area KAP-1"
elif menu == "Form Input KAP 2":
    area_aktif = "Area KAP-2"
elif menu == "Dashboard Monitoring":
    area_aktif = "Dashboard"

st.markdown(f"""
    <div style='background-color: #3B6FB6; padding: 15px; border-radius: 5px; margin-bottom: 25px;'>
        <h2 style='color: white; margin: 0;'>PT ADM - Sistem Monitoring BBM</h2>
        <p style='color: white; margin: 0;'>👤 ADMIN Logistik | {area_aktif}</p>
    </div>
""", unsafe_allow_html=True)

# ROUTING
if menu == "Portal Utama":
    render_portal()
elif menu == "Form Input KAP 1":
    render_kap1(conn)
elif menu == "Form Input KAP 2":
    render_kap2(conn)
elif menu == "Dashboard Monitoring":
    render_dashboard(conn)