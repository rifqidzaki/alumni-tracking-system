import database as db, scoring, search_simulator, pddikti_verifier, time
db.init_db()

DATA = [
    ("Bayu Firmansyah","Informatika",2021,"Malang"),
    ("Wahyu Setiawan","Fisioterapi",2020,"Malang"),
    ("Irfan Hakim","Teknik Elektro",2019,"Malang"),
    ("Dinda Permatasari","Farmasi",2023,"Malang"),
    ("Rofiq Hidayat","Hukum",2022,"Malang"),
    ("Lailatul Fitriyah","Kedokteran",2018,"Malang"),
    ("Alfian Nur","Agribisnis",2016,"Malang"),
    ("Lutfi Hakim","Akuntansi",2000,"Malang"),
    ("Novi Andriani","Sosiologi",2019,"Malang"),
    ("Rizal Firmansyah","Manajemen",2024,"Malang"),
    ("Nisa Amelia","Ilmu Komunikasi",2010,"Malang"),
    ("Zulfikar Ahmad","Hukum",2020,"Malang"),
    ("Zulfikar Ahmad Wildan","Psikologi",2020,"Malang"),
    ("Anis Sulistyowati","Agroteknologi",2002,"Malang"),
    ("Mohammad Lutfi Hakim","Manajemen",2014,"Malang"),
    ("Rini Aprilia Agustin","Pendidikan Bahasa Indonesia",2024,"Malang"),
    ("Hendra Kusuma","Hukum",2004,"Malang"),
    ("Muhammad Irfan Hakim","Sosiologi",2022,"Malang"),
    ("Anggun Dinda Permatasari","Akuntansi",2025,"Malang"),
    ("Ahmad Rizky Pratama","Informatika",2021,"Malang"),
    ("Siti Nurhaliza","Sistem Informasi",2023,"Surabaya"),
    ("Andi Prasetyo","Teknik Informatika",2021,"Jakarta"),
    ("Dewi Lestari","Informatika",2022,"Bandung"),
    ("Rizky Ramadhan","Teknik Elektro",2020,"Malang"),
    ("Fajar Maulana","Teknik Mesin",2023,"Surabaya"),
    ("Nadia Putri","Ilmu Komunikasi",2022,"Yogyakarta"),
    ("Muhammad Faisal","Manajemen",2021,"Malang"),
    ("Ayu Kartika","Akuntansi",2023,"Malang"),
    ("Budi Santoso","Informatika",2022,"Malang"),
    ("Hendra Wijaya","Teknik Informatika",2020,"Jakarta"),
    ("Rina Agustina","Sistem Informasi",2021,"Semarang"),
    ("Dimas Arya Putra","Informatika",2022,"Malang"),
    ("Laras Sekar Arum","Ilmu Komunikasi",2023,"Malang"),
    ("Yoga Prakoso","Teknik Mesin",2020,"Surabaya"),
    ("Citra Dewi Maharani","Akuntansi",2022,"Malang"),
    ("Fandi Ahmad","Manajemen",2021,"Malang"),
    ("Rahma Aulia","Informatika",2023,"Bandung"),
    ("Eko Budi Santoso","Teknik Elektro",2022,"Malang"),
    ("Nadya Safira","Sistem Informasi",2021,"Malang"),
    ("Galih Wicaksono","Teknik Informatika",2022,"Malang"),
]

print("="*70)
print("PHASE 1: INSERT 40 ALUMNI")
print("="*70)
ids = []
for nama, prodi, tahun, kota in DATA:
    email = nama.lower().replace(" ",".")+  "@alumni.umm.ac.id"
    aid = db.add_alumni(nama, prodi, tahun, kota, email)
    ids.append(aid)
    print(f"  #{aid:2d} {nama:<35} {prodi}")

print(f"\nInserted: {len(ids)}")

print("\n"+"="*70)
print("PHASE 2: TRACKING + SAVE EVIDENCE")
print("="*70)
track = []
for i,aid in enumerate(ids,1):
    a = dict(db.get_alumni_by_id(aid))
    cands = search_simulator.simulate_search(a)
    for c in cands: c["confidence_score"] = scoring.calculate_confidence(a, c)
    cands = scoring.cross_validate(cands)
    for c in cands: c["status"] = scoring.classify(c["confidence_score"])
    cands.sort(key=lambda x: x["confidence_score"], reverse=True)
    db.save_candidates(aid, cands)
    b = cands[0]
    db.save_evidence(aid,1,b["nama"],b.get("instansi",""),b.get("jabatan",""),b.get("sumber",""),b.get("link",""),b["confidence_score"])
    lbl = scoring.classify_label(b["status"])
    print(f"  [{i:2d}/40] {a['nama']:<35} {b['confidence_score']:.2f} [{lbl}]")
    track.append({"nama":a["nama"],"score":b["confidence_score"],"label":lbl})

print("\n"+"="*70)
print("PHASE 3: PDDIKTI VERIFICATION")
print("="*70)
pddk = []
for i,aid in enumerate(ids,1):
    a = dict(db.get_alumni_by_id(aid))
    r = pddikti_verifier.verify_alumni(a)
    time.sleep(0.2)
    s=r["confidence"]; uc=r["umm_results_count"]; tot=r["all_results_count"]
    bm=r.get("best_match"); nim=bm["nim"] if bm else "-"
    icon={"Terverifikasi":"V","Kemungkinan":"?","Tidak Ditemukan":"X"}.get(s,"-")
    print(f"  [{icon}][{i:2d}/40] {a['nama']:<35} {s:<17} UMM:{uc} NIM:{nim}")
    pddk.append({"nama":a["nama"],"status":s,"nim":nim,"umm":uc})

print("\n"+"="*70)
print("TABEL RINGKASAN")
print("="*70)
print(f"{'No':>3} | {'Nama':<35} | {'Score':>5} | {'Tracking':<18} | {'PDDIKTI':<17} | NIM")
print("-"*110)
for i,(t,p) in enumerate(zip(track,pddk),1):
    print(f"{i:>3} | {t['nama']:<35} | {t['score']:>5.2f} | {t['label']:<18} | {p['status']:<17} | {p['nim']}")

st = db.get_dashboard_stats()
print(f"\n{'='*70}")
print(f"Total Alumni    : {st['total']}")
print(f"Sudah Dilacak   : {st['sudah_dilacak']}")
print(f"Perlu Verifikasi: {st['perlu_verifikasi']}")
print(f"Belum Dilacak   : {st['belum_dilacak']}")
print(f"Total Evidence  : {st['evidence_count']}")
trv=sum(1 for p in pddk if p["status"]=="Terverifikasi")
mng=sum(1 for p in pddk if p["status"]=="Kemungkinan")
ntf=sum(1 for p in pddk if p["status"]=="Tidak Ditemukan")
print(f"\nPDDIKTI: Terverifikasi={trv} Kemungkinan={mng} TidakDitemukan={ntf}")
