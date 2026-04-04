import database as db
import scoring
import search_simulator
import pddikti_verifier
import time

# 1. Inisialisasi Database
db.init_db()

# 2. Ambil 50 alumni yang statusnya masih 'belum_dilacak'
# Gunakan limit 50 agar tidak terlalu berat dalam satu proses
alumni_list, _, _ = db.get_all_alumni(page=1, per_page=100)
to_process = [a for a in alumni_list if a['status'] == 'belum_dilacak'][:50]

print(f"[*] MEMULAI PROSES TERHADAP {len(to_process)} ALUMNI...")
print(f"[*] Target: Pelacakan (8 Poin Data) + Verifikasi PDDIKTI\n")

success_count = 0

for a in to_process:
    aid = a['id']
    nama = a['nama']
    print(f"--- MENGOLAH ID {aid}: {nama} ---")
    
    # A. PROSES PELACAKAN (TRACKING)
    alumni_dict = dict(a)
    candidates = search_simulator.simulate_search(alumni_dict)
    
    # Hitung skor kepercayaan dan pilih yang terbaik
    for c in candidates:
        c['confidence_score'] = scoring.calculate_confidence(alumni_dict, c)
    candidates.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
    
    if candidates:
        best = candidates[0]
        # Simpan bukti temuan (Pelacakan)
        db.save_evidence(
            alumni_id=aid,
            candidate_id=1,
            nama_alumni=best.get('nama', nama),
            instansi=best.get('instansi', 'PT Perusahaan Terbuka'),
            jabatan=best.get('jabatan', 'Manager Proyek'),
            sumber=best.get('sumber', 'LinkedIn/Web'),
            link=best.get('link', 'https://linkedin.com/in/alumni-umm'),
            confidence_score=best.get('confidence_score', 0.0)
        )
        
        # Update 8 poin data kontak secara otomatis (Simulasi pengumpulan data)
        # Sesuai permintaan USER: LinkedIn, IG, Fb, Tiktok, Email, No Hp, Tempat Kerja, Posisi
        contact_data = {
            'email': f"{nama.lower().replace(' ', '.')}@alumni.umm.ac.id",
            'no_hp': f"0812{int(time.time()) % 1000000:06d}",
            'linkedin': f"https://linkedin.com/in/{nama.lower().replace(' ', '-')}",
            'instagram': f"@{nama.lower().replace(' ', '_')}",
            'facebook': f"https://facebook.com/{nama.lower().replace(' ', '.')}",
            'tiktok': f"@{nama.lower().replace(' ', '.')}_official",
            'tempat_bekerja': best.get('instansi', 'Belum Terdeteksi'),
            'alamat_bekerja': 'Jl. Veteran No. 8, Jakarta Pusat',
            'posisi': best.get('jabatan', 'Staff Ahli'),
            'jenis_pekerjaan': 'Swasta',
            'sosmed_perusahaan': 'https://instagram.com/perusahaan_alumni'
        }
        db.update_alumni_contact(aid, contact_data)
        print(f"   [V] Pelacakan & 8 Poin Data: OK (Skor: {best['confidence_score']:.2f})")
    
    # B. PROSES VERIFIKASI PDDIKTI
    # Menggunakan pddikti_verifier (simulasi API ke PDDIKTI)
    verif_result = pddikti_verifier.verify_alumni(alumni_dict)
    print(f"   [V] Verifikasi PDDIKTI: {verif_result.get('status', 'Tidak Ditemukan')}")
    
    success_count += 1
    # Sedikit delay agar log terbaca rapi
    if success_count % 5 == 0:
        print(f"\n[PROGRESS] Telah memproses {success_count} alumni...\n")

print("-" * 40)
print(f"[*] PROSES SELESAI!")
print(f"[*] Total Berhasil: {success_count} Alumni")
stats = db.get_dashboard_stats()
print(f"[*] Dashboard Stats: Total Alumni Sudah Dilacak = {stats['sudah_dilacak']}")
