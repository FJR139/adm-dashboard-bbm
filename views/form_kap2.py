import streamlit as st
import datetime
from utils import get_stok_awal

def render_kap2(conn):
    st.markdown("<h3 style='text-align: center; color: #333333;'>Form Input Data Harian - KAP-2</h3>", unsafe_allow_html=True)
    st.write("---")

    # --- Input Tanggal (untuk backtesting & entry harian) ---
    tgl_input = st.date_input(
        "📅 Tanggal Transaksi",
        value=datetime.date.today(),
        max_value=datetime.date.today()
    )
    stok_awal_kemarin_kap2 = get_stok_awal(conn, "KAP-2", tgl_input)

    st.write("")

    col_kiri, spacer, col_kanan = st.columns([10, 1, 10])

    with col_kiri:
        st.markdown("### 1. Penerimaan (F1)")
        with st.container(border=True):
            f1_awal_in = st.number_input("Digit Awal (Liter) F1", min_value=0.0, format="%.2f", key="kap2_f1_a", value=None)
            f1_akhir_in = st.number_input("Digit Akhir (Liter) F1", min_value=0.0, format="%.2f", key="kap2_f1_b", value=None)
            f1_awal_kap2 = f1_awal_in if f1_awal_in is not None else 0.0
            f1_akhir_kap2 = f1_akhir_in if f1_akhir_in is not None else 0.0
            volume_f1_kap2 = f1_akhir_kap2 - f1_awal_kap2
            st.caption(f"Volume Masuk: {volume_f1_kap2:.2f} Liter")

        st.markdown("### 2. Level Meter")
        with st.container(border=True):
            st.caption(f"ℹ️ Stok Awal (Level Akhir Kemarin): **{stok_awal_kemarin_kap2:,.0f} Liter**")
            pv_tank1_in = st.number_input("Tank 1 (PV) Liter", min_value=0.0, format="%.2f", key="kap2_pv1", value=None)
            pv_tank1_kap2 = pv_tank1_in if pv_tank1_in is not None else 0.0

    with col_kanan:
        st.markdown("### 3. Dispenser Reguler (F3 & F4)")
        with st.container(border=True):
            f34_awal_in = st.number_input("Digit Awal (Liter)", min_value=0.0, format="%.2f", key="kap2_f34_a", value=None)
            f34_akhir_in = st.number_input("Digit Akhir (Liter)", min_value=0.0, format="%.2f", key="kap2_f34_b", value=None)
            f34_awal_kap2 = f34_awal_in if f34_awal_in is not None else 0.0
            f34_akhir_kap2 = f34_akhir_in if f34_akhir_in is not None else 0.0
            volume_f34_kap2 = f34_akhir_kap2 - f34_awal_kap2
            st.caption(f"Volume Keluar Reguler: {volume_f34_kap2:.2f} Liter")

    st.write("---")
    col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
    with col_b2:
        if st.button("SUBMIT DATA HARIAN KAP-2", use_container_width=True, type="primary", key="kap2_submit"):
            if volume_f1_kap2 < 0 or volume_f34_kap2 < 0:
                st.error("❌ Digit akhir tidak boleh lebih kecil dari digit awal!")
            elif conn is not None:
                try:
                    cur = conn.cursor()

                    # 1. Simpan Penerimaan
                    cur.execute("""INSERT INTO log_penerimaan_tangki (tanggal, id_area, kategori_sap, fm1_awal, fm1_akhir, volume_terima)
                                   VALUES (%s, %s, %s, %s, %s, %s)""",
                                (tgl_input, 'KAP-2', 'GR', f1_awal_kap2, f1_akhir_kap2, volume_f1_kap2))

                    # 2. Simpan Dispenser Reguler
                    cur.execute("""INSERT INTO log_pengeluaran_dispenser (tanggal, id_area, kategori_sap, id_flowmeter, angka_meter_awal, angka_meter_akhir, volume_keluar)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                (tgl_input, 'KAP-2', 'GI Reguler', 'F3&F4', f34_awal_kap2, f34_akhir_kap2, volume_f34_kap2))

                    # 3. Kalkulasi Loss KAP 2
                    stok_awal_aktual_kap2 = get_stok_awal(conn, 'KAP-2', tgl_input)
                    loss_kap2 = round((stok_awal_aktual_kap2 + volume_f1_kap2 - volume_f34_kap2) - pv_tank1_kap2, 2)
                    status_loss_kap2 = "SELISIH" if abs(loss_kap2) > 0.01 else "AMAN"

                    # 4. Simpan ke Daily Stock Log
                    cur.execute("""INSERT INTO daily_stock_log
                                   (tanggal, id_area, stok_awal_level_meter, total_pengisian, total_pemakaian, stok_akhir_level_meter, loss_kalkulasi, status_loss)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                   ON CONFLICT (tanggal, id_area) DO UPDATE SET
                                   stok_awal_level_meter = EXCLUDED.stok_awal_level_meter,
                                   total_pengisian = EXCLUDED.total_pengisian,
                                   total_pemakaian = EXCLUDED.total_pemakaian,
                                   stok_akhir_level_meter = EXCLUDED.stok_akhir_level_meter,
                                   loss_kalkulasi = EXCLUDED.loss_kalkulasi,
                                   status_loss = EXCLUDED.status_loss;""",
                                (tgl_input, 'KAP-2',
                                 round(stok_awal_aktual_kap2, 2), round(volume_f1_kap2, 2),
                                 round(volume_f34_kap2, 2), round(pv_tank1_kap2, 2),
                                 round(loss_kap2, 2), status_loss_kap2))

                    conn.commit()
                    cur.close()
                    st.success(f"✅ Data KAP-2 tanggal {tgl_input.strftime('%d %B %Y')} berhasil disimpan!")
                    st.balloons()
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Terjadi kesalahan database: {e}")
            else:
                st.error("Koneksi database terputus.")