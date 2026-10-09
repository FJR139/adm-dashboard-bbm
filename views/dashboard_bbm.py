import streamlit as st
import pandas as pd
import datetime

def render_dashboard(conn):
    # --- 1. AMBIL DATA DARI DATABASE ---
    try:
        query = "SELECT * FROM daily_stock_log"
        df = pd.read_sql(query, conn)
        df['tanggal'] = pd.to_datetime(df['tanggal']).dt.date
    except Exception as e:
        st.error(f"Gagal mengambil data dari database: {e}")
        df = pd.DataFrame() 

    # --- 2. CSS ---
    st.markdown("""
        <style>
            .stApp { background-color: #F4F6F9; }
            .kpi-card { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; border-top: 4px solid #005A9E; margin-bottom: 20px; }
            .kpi-title { margin: 0; color: #666; font-size: 14px; font-weight: 600; text-transform: uppercase; }
            .kpi-value { margin: 10px 0 0 0; color: #333; font-size: 24px; font-weight: bold; }
            .kpi-green { color: #28a745; }
            .kpi-orange { color: #fd7e14; }
            .alert-card { background-color: #E3000F; color: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 10px rgba(227,0,15,0.3); text-align: center; margin-bottom: 20px; }
            .tank-container { width: 250px; border: 4px solid #B0BEC5; border-radius: 5px; position: relative; background-color: #ECEFF1; margin: 0 auto; overflow: hidden; box-shadow: inset 0 0 10px rgba(0,0,0,0.1); }
            .tank-fill { position: absolute; bottom: 0; width: 100%; background: linear-gradient(to bottom, #2196F3, #0D47A1); transition: height 0.5s ease; }
            .tank-text { position: absolute; top: 40%; width: 100%; text-align: center; font-weight: bold; color: white; text-shadow: 1px 1px 3px rgba(0,0,0,0.8); z-index: 2; }
        </style>
    """, unsafe_allow_html=True)

    # --- 3. HEADER & FILTER TANGGAL ---
    st.markdown("""
        <div style='background-color: white; padding: 15px 25px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center;'>
            <h3 style='margin: 0; color: #005A9E;'>🏭 Dashboard Monitoring Stok BBM</h3>
            <p style='margin: 0; font-weight: bold; color: #E3000F;'>ADMIN Logistik | PT Astra Daihatsu Motor</p>
        </div>
    """, unsafe_allow_html=True)

    col_date, _ = st.columns([1, 4])
    with col_date:
        selected_date = st.date_input("📅 Tanggal Operasional", datetime.date(2026, 9, 30))
    st.write("") 

    # --- 4. LOGIKA PEMROSESAN DATA ---
    df_hari_ini = df[df['tanggal'] == selected_date] if not df.empty else pd.DataFrame()
    
    df_kap1 = df_hari_ini[df_hari_ini['id_area'] == 'KAP-1'] if not df_hari_ini.empty else pd.DataFrame()
    df_kap2 = df_hari_ini[df_hari_ini['id_area'] == 'KAP-2'] if not df_hari_ini.empty else pd.DataFrame()

    k1_awal = df_kap1['stok_awal_level_meter'].sum() if not df_kap1.empty else 0
    k1_terima = df_kap1['total_pengisian'].sum() if not df_kap1.empty else 0
    k1_pakai = df_kap1['total_pemakaian'].sum() if ('total_pemakaian' in df_kap1.columns and not df_kap1.empty) else 0 
    k1_akhir = df_kap1['stok_akhir_level_meter'].sum() if not df_kap1.empty else 0
    k1_loss = df_kap1['loss_kalkulasi'].sum() if ('loss_kalkulasi' in df_kap1.columns and not df_kap1.empty) else 0

    k2_awal = df_kap2['stok_awal_level_meter'].sum() if not df_kap2.empty else 0
    k2_terima = df_kap2['total_pengisian'].sum() if not df_kap2.empty else 0
    k2_pakai = df_kap2['total_pemakaian'].sum() if ('total_pemakaian' in df_kap2.columns and not df_kap2.empty) else 0
    k2_akhir = df_kap2['stok_akhir_level_meter'].sum() if not df_kap2.empty else 0
    k2_loss = df_kap2['loss_kalkulasi'].sum() if ('loss_kalkulasi' in df_kap2.columns and not df_kap2.empty) else 0


    # --- 5. TABS AREA (UI) ---
    tab1, tab2 = st.tabs(["📍 Area KAP 1", "📍 Area KAP 2"])
    kapasitas_max = 20000

    # ================= TAB 1: KAP 1 =================
    with tab1:
        st.write("### Data Operasional - KAP 1")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<div class='kpi-card'><p class='kpi-title'>Stok Awal</p><h3 class='kpi-value'>{k1_awal:,.0f} L</h3></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='kpi-card'><p class='kpi-title'>Penerimaan</p><h3 class='kpi-value kpi-green'>+ {k1_terima:,.0f} L</h3></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='kpi-card'><p class='kpi-title'>Pemakaian</p><h3 class='kpi-value kpi-orange'>- {k1_pakai:,.0f} L</h3></div>", unsafe_allow_html=True)
        with c4:
            if k1_loss > 0:
                st.markdown(f"""
                    <div class='alert-card'>
                        <p style='margin: 0; font-size: 13px; font-weight: bold;'>Selisih Stok vs Level Meter</p>
                        <h2 style='margin: 10px 0; font-size: 32px;'>- {k1_loss:,.0f} L</h2>
                        <p style='margin: 0; font-size: 11px;'>⚠️ MISMATCH - CEK KEBOCORAN/SALAH INPUT</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='kpi-card' style='border-top: 4px solid #28a745;'>
                        <p class='kpi-title'>Selisih Stok vs Level Meter</p>
                        <h3 class='kpi-value kpi-green'>0 L</h3>
                        <p style='margin: 0; font-size: 11px; color: #28a745; font-weight: bold;'>✅ STATUS AMAN</p>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()
        
        persen_isi_k1 = min(int((k1_akhir / kapasitas_max) * 100), 100) if kapasitas_max > 0 else 0

        
        _, col_tank_k1, _ = st.columns([1, 2, 1])
        with col_tank_k1:
            st.markdown("<h4 style='text-align: center; color: #555;'>Storage Tank KAP 1</h4>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class='tank-container' style='height: 300px;'>
                    <div class='tank-fill' style='height: {persen_isi_k1}%;'></div>
                    <div class='tank-text'>Level Meter<br>{k1_akhir:,.0f} L</div>
                </div>
            """, unsafe_allow_html=True)

    # ================= TAB 2: KAP 2 =================
    with tab2:
        st.write("### Data Operasional - KAP 2")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<div class='kpi-card'><p class='kpi-title'>Stok Awal</p><h3 class='kpi-value'>{k2_awal:,.0f} L</h3></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='kpi-card'><p class='kpi-title'>Penerimaan</p><h3 class='kpi-value kpi-green'>+ {k2_terima:,.0f} L</h3></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='kpi-card'><p class='kpi-title'>Pemakaian</p><h3 class='kpi-value kpi-orange'>- {k2_pakai:,.0f} L</h3></div>", unsafe_allow_html=True)
        with c4:
            if k2_loss > 0:
                st.markdown(f"""
                    <div class='alert-card'>
                        <p style='margin: 0; font-size: 13px; font-weight: bold;'>Selisih Stok vs Level Meter</p>
                        <h2 style='margin: 10px 0; font-size: 32px;'>- {k2_loss:,.0f} L</h2>
                        <p style='margin: 0; font-size: 11px;'>⚠️ MISMATCH</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='kpi-card' style='border-top: 4px solid #28a745;'>
                        <p class='kpi-title'>Selisih Stok vs Level Meter</p>
                        <h3 class='kpi-value kpi-green'>0 L</h3>
                        <p style='margin: 0; font-size: 11px; color: #28a745; font-weight: bold;'>✅ STATUS AMAN</p>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()
        
        persen_isi_k2 = min(int((k2_akhir / kapasitas_max) * 100), 100) if kapasitas_max > 0 else 0

        _, col_tank_k2, _ = st.columns([1, 2, 1])
        with col_tank_k2:
            st.markdown("<h4 style='text-align: center; color: #555;'>Storage Tank KAP 2</h4>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class='tank-container' style='height: 300px;'>
                    <div class='tank-fill' style='height: {persen_isi_k2}%;'></div>
                    <div class='tank-text'>Level Meter<br>{k2_akhir:,.0f} L</div>
                </div>
            """, unsafe_allow_html=True)