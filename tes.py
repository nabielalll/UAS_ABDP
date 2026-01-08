import http.client
import json
from typing import List, Dict

# ==========================================================
# 1. KONFIGURASI API (PATH TERAKHIR YANG TERBUKTI BERHASIL DI LANGKAH 1)
# ==========================================================
# GANTI JIKA PERLU
RAPIDAPI_KEY = "22432884dfmsh0066bc20532578bp122571jsn38d89bbd824b" 
RAPIDAPI_HOST = "tennis-api-atp-wta-itf.p.rapidapi.com"

# PATH YANG TERBUKTI BERFUNGSI di Langkah 1
RANKING_PATH = "/tennis/v2/atp/player/" 

SURFACE_SUMMARY_PATH = "/tennis/v2/atp/player/surface-summary/"

HEADERS = {
    'x-rapidapi-key': RAPIDAPI_KEY,
    'x-rapidapi-host': RAPIDAPI_HOST
}

# ==========================================================
# 2. FUNGSI PEMBANTU
# ==========================================================
def call_api(path: str) -> dict:
    """Fungsi pembantu untuk memanggil API dan menangani respons."""
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    
    try:
        conn.request("GET", path, headers=HEADERS)
        res = conn.getresponse()
        
        if res.status != 200:
            error_data = res.read().decode("utf-8")
            print(f"\n[ERROR {res.status}] Gagal memanggil {path}: {res.reason}")
            print(f"Pesan dari Server: {error_data[:100]}...")
            return {}

        data = res.read().decode("utf-8")
        if not data:
            return {}
        return json.loads(data)
        
    except Exception as e:
        print(f"\n[ERROR KONEKSI] Gagal memanggil {path}: {e}")
        return {}
    finally:
        conn.close()

# ==========================================================
# 3. FUNGSI UTAMA (PENGAMBILAN DATA)
# ==========================================================
def get_top_player_ids() -> List[Dict]:
    """Mengambil ID dan Nama pemain yang tersedia dari endpoint /player/."""
    print(f"Langkah 1: Mengambil ID pemain dari endpoint {RANKING_PATH}...")
    data = call_api(RANKING_PATH)
    
    players_raw = data.get('data', [])
    
    top_20_ids = []
    
    for player in players_raw[:20]:
        top_20_ids.append({
            'id': player.get('id'),
            'name': player.get('name')
        })
        
    print(f"Ditemukan {len(top_20_ids)} ID pemain.")
    return top_20_ids

def calculate_win_rate(top_players: List[Dict]) -> List[Dict]:
    """Menghitung Win Rate menggunakan field 'courtWins'/'courtLosses'."""
    final_stats = []
    
    for player_info in top_players:
        player_id = player_info.get('id')
        player_name = player_info.get('name')
        
        if not player_id: continue 

        path = f"{SURFACE_SUMMARY_PATH}{player_id}" 
        stats_data = call_api(path)
        
        # Data statistik per permukaan adalah LIST per tahun
        data_per_year = stats_data.get('data', []) 
        
        total_wins = 0
        total_losses = 0
        
        # Iterasi TINGKAT 1: Melalui setiap tahun (year_stats)
        for year_stats in data_per_year:
            if isinstance(year_stats, dict):
                # Iterasi TINGKAT 2: Melalui list 'surfaces' dalam tahun tersebut
                surfaces = year_stats.get('surfaces', [])
                
                for surface_stats in surfaces:
                    if isinstance(surface_stats, dict):
                        # Menggunakan field 'courtWins'/'courtLosses' yang benar
                        total_wins += surface_stats.get('courtWins', 0)
                        total_losses += surface_stats.get('courtLosses', 0)
            
        total_matches = total_wins + total_losses
        
        win_rate = (total_wins / total_matches) * 100 if total_matches > 0 else 0.0

        final_stats.append({
            'Nama Pemain': player_name,
            'Win Rate': win_rate,
            'Menang': total_wins,
            'Kalah': total_losses
        })

    valid_players = [p for p in final_stats if p['Menang'] > 0]
    return sorted(valid_players, key=lambda x: x['Win Rate'], reverse=True)

# ==========================================================
# 5. PROGRAM UTAMA (EKSEKUSI)
# ==========================================================

if __name__ == "__main__":
    
    print("--- Analisis Win Rate Pemain yang Data Statistiknya Tersedia di API ---")
    
    # 1. Ambil ID pemain top
    top_players = get_top_player_ids()
    
    if top_players:
        # 2. Ambil statistik dan hitung Win Rate
        final_ranking = calculate_win_rate(top_players)
        
        # 3. Tampilkan Hasil
        top_20_final = final_ranking[:20]
        
        print("\n--- RANKING POPULARITAS KINERJA BERDASARKAN WIN RATE ---")
        print(f"Analisis dari {len(top_20_final)} Pemain yang tersedia statistiknya.")
        print("-" * 75)
        print("{:<5} {:<30} {:<15} {:<10} {:<10}".format("Rank", "Nama Pemain", "Win Rate (%)", "Menang", "Kalah"))
        print("-" * 75)
        
        for i, player in enumerate(top_20_final):
            print("{:<5} {:<30} {:<15.2f} {:<10} {:<10}".format(
                i + 1, 
                player['Nama Pemain'], 
                player['Win Rate'], 
                player['Menang'], 
                player['Kalah']
            ))
    else:
        print("\n[GAGAL TOTAL] Tidak ada data pemain yang bisa diproses. (Cek Langganan API)")