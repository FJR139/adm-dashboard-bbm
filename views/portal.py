import streamlit as st

def render_portal():
    st.markdown("<h3 style='text-align: center;'>Selamat Datang di Portal Monitoring Stok</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Pilih Area Operasional untuk mengakses form input stok atau lihat dashboard hari ini.</p>", unsafe_allow_html=True)
    st.write("---")

    col1, spacer, col2 = st.columns([5, 1, 5])

    with col1:
        with st.container(border=True):
            st.markdown("### 🏭 KAP 1")
            st.markdown("**Fuel Slow Station**")
            st.markdown("Fuel Daily Tank")
            st.markdown("Dispenser")
            if st.button("Masuk ke KAP 1", use_container_width=True, type="primary", key="portal_kap1"):
                st.session_state.selected_menu = "Form Input KAP 1"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### 🏭 KAP 2")
            st.markdown("**Fuel Slow Station**")
            st.markdown("Fuel Daily Tank")
            st.markdown("Dispenser")
            if st.button("Masuk ke KAP 2", use_container_width=True, type="primary", key="portal_kap2"):
                st.session_state.selected_menu = "Form Input KAP 2"
                st.rerun()