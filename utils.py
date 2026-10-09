import streamlit as st

def get_stok_awal(conn, id_area, tgl_input):
    """Mengambil stok_akhir_level_meter hari terakhir sebelum tgl_input."""
    if conn is None:
        return 0.0
    try:
        cur = conn.cursor()
        query = """
            SELECT stok_akhir_level_meter 
            FROM daily_stock_log 
            WHERE id_area = %s AND tanggal < %s 
            ORDER BY tanggal DESC 
            LIMIT 1;
        """
        cur.execute(query, (id_area, tgl_input))
        result = cur.fetchone()
        cur.close()
        if result and result[0] is not None:
            return float(result[0])
        return 0.0
    except Exception as e:
        return 0.0

