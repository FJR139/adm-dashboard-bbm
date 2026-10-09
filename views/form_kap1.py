import streamlit as st
import datetime
from utils import get_stok_awal

def render_kap1(conn):
    st.markdown("<h3 style='text-align: center; color: #333333;'>Form Input Data Harian - KAP-1</h3>", unsafe_allow_html=True)
    st.write("---")

    # --- Input Tanggal (untuk backtesting & entry harian) ---
    tgl_input = st.date_input(
        "📅 Tanggal Transaksi",
        value=datetime.date.today(),
        max_value=datetime.date.today()
    )
    stok_awal_kemarin = get_stok_awal(conn, "KAP-1", tgl_input)

    st.write("")

    col_kiri, spacer, col_kanan = st.columns([10, 1, 10])

    with col_kiri:
        st.markdown("### 1. Penerimaan (FM1)")
        with st.container(border=True):
            f1_awal = st.number_input("Digit Awal (Liter)", min_value=0.0, format="%.2f", key="kap1_f1_a")
            f1_akhir = st.number_input("Digit Akhir (Liter)", min_value=0.0, format="%.2f", key="kap1_f1_b")
            volume_f1 = f1_akhir - f1_awal
            st.caption(f"Volume Masuk: {volume_f1:.2f} Liter")

        st.markdown("### 2. Transfer Internal (FM2)")
        with st.container(border=True):
            fm2_awal = st.number_input("Digit Awal FM2 (Liter)", min_value=0.0, format="%.2f", key="kap1_fm2_a")
            fm2_akhir = st.number_input("Digit Akhir FM2 (Liter)", min_value=0.0, format="%.2f", key="kap1_fm2_b")
            volume_fm2 = fm2_akhir - fm2_awal
            st.caption(f"Volume Transfer Internal: {volume_fm2:.2f} Liter")

        st.markdown("### 3. Level Meter")
        col1, col2 = st.columns(2)
    
    with col1:
        tank1_input = st.number_input("Tanki 1 (PV)", min_value=0.0, step=0.1, value=None)
        tank2_input = st.number_input("Tanki 2 (PV)", min_value=0.0, step=0.1, value=None)
        daily_tank_input = st.number_input("Daily Tank (PV)", min_value=0.0, step=0.1, value=None)
    
    val_tank1 = tank1_input if tank1_input is not None else 0.0
    val_tank2 = tank2_input if tank2_input is not None else 0.0
    val_daily = daily_tank_input if daily_tank_input is not None else 0.0
    
    daily_tank_actual = val_daily * 2
    total_storage = val_tank1 + val_tank2 + daily_tank_actual

    with col2:
        st.write("### Total Kalkulasi")
        st.metric(label="Total Storage (Liter)", value=f"{total_storage:.1f}")
        st.info(f"💡 Info: Nilai Daily Tank otomatis dikali 2 ({val_daily} x 2 = {daily_tank_actual})")

    st.write("---")

    with col_kanan:
        st.markdown("### 4. Dispenser Reguler (F3 & F4)")
        with st.container(border=True):
            f34_awal = st.number_input("Digit Awal (Liter) F3&F4", min_value=0.0, format="%.2f", key="kap1_f34_a")
            f34_akhir = st.number_input("Digit Akhir (Liter) F3&F4", min_value=0.0, format="%.2f", key="kap1_f34_b")
            volume_f34 = f34_akhir - f34_awal
            st.caption(f"Volume Keluar Reguler: {volume_f34:.2f} Liter")

        st.markdown("### 5. Dispenser Non-Reguler (F5)")
        with st.container(border=True):
            job_codes = {"Pilih Job Code": 0.0, "Job Code 1 (3000 mL)": 3.0, "Job Code 5 (5000 mL)": 5.0}
            pilihan_job = st.selectbox("Pengujian:", options=list(job_codes.keys()), key="kap1_jobcode")
            volume_f5 = job_codes[pilihan_job]
            st.caption(f"Volume Keluar Non-Reguler: {volume_f5:.2f} Liter")
        st.subheader("6. Totalisator OUT ASSY")
        totalisator_out_assy_input = st.number_input("Input Totalisator OUT ASSY", min_value=0.0, step=0.1)

    st.write("---")
    col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
    with col_b2:
        if st.button("SUBMIT DATA HARIAN KAP-1", use_container_width=True, type="primary", key="kap1_submit"):
            if volume_f1 < 0 or volume_f34 < 0 or volume_fm2 < 0:
                st.error("❌ Digit akhir tidak boleh lebih kecil dari digit awal!")
            elif conn is not None:
                try:
                    cur = conn.cursor()

                    # 1. Simpan Penerimaan Tangki (FM1)
                    cur.execute("""INSERT INTO log_penerimaan_tangki (tanggal, id_area, kategori_sap, fm1_awal, fm1_akhir, volume_terima)
                                   VALUES (%s, %s, %s, %s, %s, %s)""",
                                (tgl_input, 'KAP-1', 'GR', f1_awal, f1_akhir, volume_f1))

                    # 2. Simpan Transfer Internal (FM2)
                    cur.execute("""INSERT INTO log_transfer_internal (tanggal, id_area, fm2_awal, fm2_akhir, volume_transfer)
                                   VALUES (%s, %s, %s, %s, %s)""",
                                (tgl_input, 'KAP-1', fm2_awal, fm2_akhir, volume_fm2))

                    # 3. Simpan Dispenser Reguler (F3 & F4)
                    cur.execute("""INSERT INTO log_pengeluaran_dispenser (tanggal, id_area, kategori_sap, id_flowmeter, angka_meter_awal, angka_meter_akhir, volume_keluar)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                (tgl_input, 'KAP-1', 'GI Reguler', 'F3&F4', f34_awal, f34_akhir, volume_f34))

                    # 4. Simpan Dispenser Non-Reguler (F5) jika ada pengujian
                    if volume_f5 > 0:
                        cur.execute("""INSERT INTO log_pengeluaran_dispenser (tanggal, id_area, kategori_sap, id_flowmeter, angka_meter_awal, angka_meter_akhir, volume_keluar)
                                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                    (tgl_input, 'KAP-1', 'GI Non-Reguler', 'F5', 0, 0, volume_f5))

                    val_tank1 = tank1_input if tank1_input is not None else 0.0
                    val_tank2 = tank2_input if tank2_input is not None else 0.0
                    val_daily = daily_tank_input if daily_tank_input is not None else 0.0
                    
                    # 5. Kalkulasi Loss & Simpan ke Daily Stock Log
                    total_pakai = volume_f34 + volume_f5
                    stok_akhir_aktual = total_storage
                    stok_awal_aktual = get_stok_awal(conn, 'KAP-1', tgl_input)
                    loss = round((stok_awal_aktual + volume_f1 - total_pakai) - stok_akhir_aktual, 2)
                    status_loss = "SELISIH" if abs(loss) > 0.01 else "AMAN"

                    cur.execute("""INSERT INTO daily_stock_log
                                   (tanggal, id_area, stok_awal_level_meter, total_pengisian, total_pemakaian, stok_akhir_level_meter, loss_kalkulasi, status_loss, tank1_level, tank2_level, daily_tank_level, total_storage_level, totalisator_out_assy)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                   ON CONFLICT (tanggal, id_area) DO UPDATE SET
                                   stok_awal_level_meter = EXCLUDED.stok_awal_level_meter,
                                   total_pengisian = EXCLUDED.total_pengisian,
                                   total_pemakaian = EXCLUDED.total_pemakaian,
                                   stok_akhir_level_meter = EXCLUDED.stok_akhir_level_meter,
                                   loss_kalkulasi = EXCLUDED.loss_kalkulasi,
                                   status_loss = EXCLUDED.status_loss,
                                   tank1_level = EXCLUDED.tank1_level,
                                   tank2_level = EXCLUDED.tank2_level,
                                   daily_tank_level = EXCLUDED.daily_tank_level,
                                   total_storage_level = EXCLUDED.total_storage_level,
                                   totalisator_out_assy = EXCLUDED.totalisator_out_assy;""",
                                (
                                tgl_input, 'KAP-1',
                                round(stok_awal_aktual, 2), round(volume_f1, 2),
                                round(total_pakai, 2), round(stok_akhir_aktual, 2),
                                round(loss, 2), status_loss,
                                val_tank1, val_tank2, daily_tank_actual, total_storage, totalisator_out_assy_input)
                                 )
                    conn.commit()
                    cur.close()
                    st.success(f"✅ Data KAP-1 tanggal {tgl_input.strftime('%d %B %Y')} berhasil disimpan!")
                    st.balloons()
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Terjadi kesalahan database: {e}")
            else:
                st.error("Koneksi database terputus.")