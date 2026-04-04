import database as db
import scoring
import search_simulator
import time

# Inisialisasi DB
db.init_db()

# Ambil alumni dari daftar awal yang masih 'belum_dilacak'
alumni_list, _, _ = db.get_all_alumni(page=1, per_page=50)
to_track = [a for a in alumni_list if a['status'] == 'belum_dilacak'][:10]

print(f"[*] Menjalankan pelacakan untuk {len(to_track)} alumni...")

for a in to_track:
    aid = a['id']
    nama = a['nama']
    print(f"\n--- Melacak: {nama} (ID: {aid}) ---")
    
    # 1. Simulasi Search
    alumni_dict = dict(a)
    candidates = search_simulator.simulate_search(alumni_dict)
    
    # 2. Scoring & Validation
    for c in candidates:
        c['confidence_score'] = scoring.calculate_confidence(alumni_dict, c)
    
    # 3. Urutkan berdasarkan skor tertinggi
    candidates.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
    
    # 4. Simpan Kandidat ke DB
    db.save_candidates(aid, candidates)
    
    # 5. Simpan Evidence (Pilih kandidat terbaik)
    if candidates:
        best = candidates[0]
        # Pastikan status kandidat match
        best['status'] = scoring.classify(best['confidence_score'])
        
        db.save_evidence(
            alumni_id=aid,
            candidate_id=1,  # Default ID
            nama_alumni=best.get('nama', nama),
            instansi=best.get('instansi', ''),
            jabatan=best.get('jabatan', ''),
            sumber=best.get('sumber', 'LinkedIn/Google'),
            link=best.get('link', ''),
            confidence_score=best.get('confidence_score', 0.0)
        )
        print(f"   [OK] Evidence disimpan dengan skor: {best['confidence_score']:.2f}")
    else:
        print(f"   [!] Tidak ada kandidat ditemukan.")

# Update Stats
stats = db.get_dashboard_stats()
print(f"\n[DONE] Total Alumni Sudah Dilacak: {stats['sudah_dilacak']}")
