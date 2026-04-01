"""Find 2 more UMM students."""
import pddikti_verifier, database as db, time
db.init_db()

existing = db.get_all_alumni(page=1, per_page=100)
existing_names = set(dict(a)["nama"].upper() for a in existing[0])
found = []

for name in ["Taufik Hidayat", "Zulfikar Ahmad", "Retno Palupi", "Aisyah Putri", "Bagus Setiawan"]:
    if len(found) >= 2:
        break
    results = pddikti_verifier.search_mahasiswa(name)
    time.sleep(0.3)
    for r in results:
        if len(found) >= 2:
            break
        nim = r.get("nim", "")
        nama_up = r["nama"].upper()
        if nim and nama_up not in existing_names and pddikti_verifier.is_umm_student(r):
            existing_names.add(nama_up)
            found.append(r)
            nama = r["nama"].title()
            prodi = r.get("nama_prodi", "Informatika").title()
            aid = db.add_alumni(nama, prodi, 2022, "Malang", nama.lower().replace(" ", ".") + "@alumni.umm.ac.id")
            alumni = db.get_alumni_by_id(aid)
            result = pddikti_verifier.verify_alumni(dict(alumni))
            time.sleep(0.3)
            confidence = result["confidence"]
            umm_c = result["umm_results_count"]
            print(f"  #{aid} [{confidence}] {nama} NIM:{nim} Prodi:{prodi} UMM:{umm_c}")

stats = db.get_dashboard_stats()
print(f"Total alumni: {stats['total']}")
