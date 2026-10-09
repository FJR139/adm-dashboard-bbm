import pandas as pd
import psycopg2
from datetime import date
import numpy as np

def import_excel_to_db():
    # Nama file Excel asli
    file_path = "DAILY FAJAR BBM.xlsx"
    
    print("⏳ Membaca file Excel...")
    try:
        # Membaca tanpa header agar kita bisa mengakses baris dan kolom secara absolut (koordinat)
        df = pd.read_excel(file_path, sheet_name='Stock Daily BBM', header=None)
        
        # Koneksi ke PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            database="adm_logistic_fuel",
            user="postgres",
            password="fajar123",
            port="5432"
        )
        cur = conn.cursor()
        
        # Bersihkan hanya data September 15-30 (tidak menghapus data lain)
        cur.execute("DELETE FROM daily_stock_log WHERE tanggal BETWEEN '2026-09-15' AND '2026-09-30';")
        print("🗑️  Data lama September 15-30 berhasil dibersihkan.")
        
        # Titik awal stok berjalan pada 14 September (berdasarkan data Excel baris 5 dan 9)
        stok_berjalan_kap1 = 22228.00
        stok_berjalan_kap2 = 19523.09
        
        print("🚀 Memulai ekstraksi dan transformasi data (15-30 September)...")
        
        # Looping untuk tanggal 15 sampai 30
        # Dalam Excel Anda, kolom indeks ke-15 mewakili tanggal 15
        for day in range(15, 31):
            col_idx = day
            current_date = date(2026, 9, day)

            # ========================
            # 1. PROSES DATA KAP-1
            # ========================
            stok_awal_k1  = stok_berjalan_kap1
            stok_akhir_k1 = df.iloc[6, col_idx]  # Baris ke-7 (indeks 6) = Stok Akhir KAP-1
            
            kap1_diproses = False

            # Jika hari libur / tidak ada pencatatan, skip hanya KAP-1
            if not pd.isna(stok_akhir_k1):
                # Deteksi Pengisian 
                before_k1  = df.iloc[8, col_idx]
                after_k1   = df.iloc[9, col_idx]
                pengisian_k1 = 0.0
                if not pd.isna(before_k1) and not pd.isna(after_k1):
                    pengisian_k1 = float(after_k1) - float(before_k1)
                    
                # Deteksi Pemakaian Flowmeter 
                pemakaian_k1 = df.iloc[7, col_idx]
                if pd.isna(pemakaian_k1):
                    # Jika flowmeter kosong, hitung pemakaian berdasarkan selisih stok 
                    pemakaian_k1 = (stok_awal_k1 + pengisian_k1) - float(stok_akhir_k1)
                
                # Hitung Loss & Statusnya
                loss_k1        = round((stok_awal_k1 + pengisian_k1 - float(pemakaian_k1)) - float(stok_akhir_k1), 2)
                status_loss_k1 = "SELISIH" if abs(loss_k1) > 0.01 else "AMAN"
                
                # Simpan ke Database
                cur.execute("""
                    INSERT INTO daily_stock_log 
                    (tanggal, id_area, stok_awal_level_meter, total_pengisian, total_pemakaian, stok_akhir_level_meter, loss_kalkulasi, status_loss)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (current_date, 'KAP-1', round(stok_awal_k1, 2), round(pengisian_k1, 2),
                      round(float(pemakaian_k1), 2), round(float(stok_akhir_k1), 2),
                      loss_k1, status_loss_k1))
                
                # Update stok berjalan untuk hari berikutnya 
                stok_berjalan_kap1 = float(stok_akhir_k1)
                kap1_diproses = True
                print(f"  ✔ KAP-1 {current_date} | Stok Akhir: {stok_akhir_k1} | Loss: {loss_k1} | {status_loss_k1}")
            else:
                print(f"  ⏭ KAP-1 {current_date} dilewati (data kosong)")

            # 2. PROSES DATA KAP-2
        
            stok_awal_k2  = stok_berjalan_kap2
            stok_akhir_k2 = df.iloc[10, col_idx]  # Baris ke-11 (indeks 10) = Stok Akhir KAP-2
            
            if not pd.isna(stok_akhir_k2):
                # Karena KAP-2 di Excel tidak merinci pengisian/pemakaian harian,
                # kita simulasikan selisih murni sebagai total pemakaian
                pengisian_k2 = 0.0
                pemakaian_k2 = round((stok_awal_k2 + pengisian_k2) - float(stok_akhir_k2), 2)
                loss_k2        = 0.0
                status_loss_k2 = "AMAN"
                
                # Simpan ke Database
                cur.execute("""
                    INSERT INTO daily_stock_log 
                    (tanggal, id_area, stok_awal_level_meter, total_pengisian, total_pemakaian, stok_akhir_level_meter, loss_kalkulasi, status_loss)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (current_date, 'KAP-2', round(stok_awal_k2, 2), round(pengisian_k2, 2),
                      round(pemakaian_k2, 2), round(float(stok_akhir_k2), 2),
                      loss_k2, status_loss_k2))
                
                # Update stok berjalan 
                stok_berjalan_kap2 = float(stok_akhir_k2)
                print(f"  ✔ KAP-2 {current_date} | Stok Akhir: {stok_akhir_k2} | Pemakaian: {pemakaian_k2}")
            else:
                print(f"  ⏭ KAP-2 {current_date} dilewati (data kosong)")
            
        conn.commit()
        print("\n✅ SELESAI! Data operasional asli ADM (September 2026) berhasil diimpor ke PostgreSQL.")
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"❌ Terjadi kesalahan: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    import_excel_to_db()