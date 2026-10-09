import psycopg2
from datetime import date, timedelta 
import random

def generate_september_data():
    try:

        conn = psycopg2.connect(
            host="Localhost",
                        database="adm_logistic_fuel",
                        user="postgres",
                        password="fajar123",
                        port="5432"
        )
        
        cur = conn.cursor()

        start_date = date(2026, 9, 15)
        end_date = date(2026, 9, 30)
        delta = timedelta(days=1)


        stok_berjalan = {"KAP-1": 65000.0, "KAP-2": 45000.0}

        current_date = start_date
        while current_date <= end_date:
            for area in ["KAP-1", "KAP-2"]:
                stok_awal = stok_berjalan[area]


                pengisian = random.choice([0, 0, 16000])


                pemakaian = random.uniform(2000.0, 8000.0)


                loss = random.choice([0.0, 0.0, 0.0, 0.05, -0.02, 1.5])
                status_loss = "SELISIH" if abs(loss) > 0.01 else "AMAN"


                stok_akhir = (stok_awal + pengisian - pemakaian) - loss
                stok_berjalan[area] = stok_akhir


                cur.execute("""
                    INSERT INTO daily_stock_log
                    (tanggal, id_area, stok_awal_level_meter, total_pengisian, total_pemakaian, stok_akhir_level_meter, loss_kalkulasi, status_loss)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (current_date, area, round(stok_awal, 2), round(pengisian, 2), round(pemakaian), round(stok_akhir), round(loss, 2),status_loss))

            current_date += delta

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Berhasil! Data dummy KAP-1 & KAP-2 dari 15-30 September 2026 telah di-generate.")

    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")

if __name__ == "__main__":
    generate_september_data()