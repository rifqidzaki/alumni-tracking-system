import database as db
import scoring
import search_simulator
import pddikti_verifier
import time

# 1. Inisialisasi Database
db.init_db()

# 2. Ambil 500 alumni yang statusnya masih 'belum_dilacak'
alumni_list, _, _ = db.get_all_alumni(page=1, per_page=1000)
to_process = [a for a in alumni_list if a['status'] == 'belum_dilacak'][:500]

print(f"[*] MEMULAI PROSES TERHADAP {len(to_process)} ALUMNI...")
print(f"[*] Target: Pelacakan (8 Poin Data) + Verifikasi PDDIKTI Batch 500\n")

success_count = 0
start_time = time.time()

for a in to_process:
    aid = a['id']
    nama = a['nama']
    
    # A. PROSES PELACAKAN (TRACKING)
    alumni_dict = dict(a)
    candidates = search_simulator.simulate_search(alumni_dict)
    
    # Hitung skor kepercayaan dan pilih yang terbaik
    for c in candidates:
        c['confidence_score'] = scoring.calculate_confidence(alumni_dict, c)
    candidates.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
    
    if candidates:
        best = candidates[0]
        # Simpan bukti temuan
        db.save_evidence(
            alumni_id=aid,
            candidate_id=1,
            nama_alumni=best.get('nama', nama),
            instansi=best.get('instansi', 'PT Global Solusi'),
            jabatan=best.get('jabatan', 'Regional Manager'),
            sumber=best.get('sumber', 'LinkedIn/Google'),
            link=best.get('link', 'https://linkedin.com/in/alumni-umm'),
            confidence_score=best.get('confidence_score', 0.0)
        )
        
        # Update 8 poin data kontak
        contact_data = {
            'email': f"{nama.lower().replace(' ', '.')}@alumni.umm.ac.id",
            'no_hp': f"0811{int(time.time()) % 1000000:06d}",
            'linkedin': f"https://linkedin.com/in/{nama.lower().replace(' ', '-')}",
            'instagram': f"@{nama.lower().replace(' ', '_')}",
            'facebook': f"https://facebook.com/{nama.lower().replace(' ', '.')}",
            'tiktok': f"@{nama.lower().replace(' ', '.')}_global",
            'tempat_bekerja': best.get('instansi', 'PT Sukses Mandiri'),
            'alamat_bekerja': 'Central Business District, Jakarta',
            'posisi': best.get('jabatan', 'Manager Head'),
            'jenis_pekerjaan': 'Swasta',
            'sosmed_perusahaan': 'https://linkedin.com/company/global_corp'
        }
        db.update_alumni_contact(aid, contact_data)
    
    # B. PROSES VERIFIKASI PDDIKTI
    pddikti_verifier.verify_alumni(alumni_dict)
    
    success_count += 1
    if success_count % 50 == 0:
        elapsed = time.time() - start_time
        print(f"[PROGRESS] {success_count}/500 alumni diproses... ({elapsed:.1f} detik)")

print("-" * 40)
print(f"[*] PROSES BATCH 500 SELESAI!")
stats = db.get_dashboard_stats()
print(f"[*] Total Alumni Sudah Dilacak = {stats['sudah_dilacak']}")
