"""Find 10 more UMM students using very specific full names."""
import pddikti_verifier
import database as db
import time

db.init_db()

# Use very specific multi-word names that are more unique
search_names = [
    "Dinda Permatasari",
    "Achmad Fauzan",
    "Rofiq Hidayat",
    "Fitriani Rahmawati",
    "Bagus Dwi",
    "Lailatul Fitriyah",
    "Alfian Nur",
    "Lutfi Hakim",
    "Anisa Rahmah",
    "Deni Setiawan",
    "Rio Febrianto",
    "Yuli Astuti",
    "Ilham Maulana",
    "Tika Wulandari",
    "Hafidz Ramadhan",
    "Sinta Dewi",
    "Gilang Ramadhan",
    "Mega Puspita",
    "Farhan Maulana",
    "Anis Sulistyowati",
]

umm_students = []
seen = set()

# Get existing names
existing = db.get_all_alumni(page=1, per_page=100)
existing_names = set()
for a in existing[0]:
    existing_names.add(dict(a)["nama"].upper())

print("Searching for more UMM students with specific names...")
for name in search_names:
    if len(umm_students) >= 10:
        break
    results = pddikti_verifier.search_mahasiswa(name)
    time.sleep(0.3)
    for r in results:
        if len(umm_students) >= 10:
            break
        nim = r.get("nim", "")
        nama_upper = r.get("nama", "").upper()
        if nim in seen or nama_upper in existing_names:
            continue
        if pddikti_verifier.is_umm_student(r):
            seen.add(nim)
            existing_names.add(nama_upper)
            umm_students.append(r)
            print(f"  FOUND: {r['nama']} | NIM: {nim} | Prodi: {r.get('nama_prodi','?')}")

print(f"\nFound {len(umm_students)} more UMM students.")

PRODI_MAP = {
    "TEKNIK INFORMATIKA": "Teknik Informatika",
    "INFORMATIKA": "Informatika",
    "SISTEM INFORMASI": "Sistem Informasi",
    "TEKNIK ELEKTRO": "Teknik Elektro",
    "TEKNIK MESIN": "Teknik Mesin",
    "ILMU KOMUNIKASI": "Ilmu Komunikasi",
    "MANAJEMEN": "Manajemen",
    "AKUNTANSI": "Akuntansi",
}

def map_prodi(p):
    up = p.upper().strip()
    for key, val in PRODI_MAP.items():
        if key in up:
            return val
    return p.title()

print("\nInserting and verifying...")
for s in umm_students:
    nama = s["nama"].title()
    prodi = map_prodi(s.get("nama_prodi", "Informatika"))
    kota = "Malang"
    email = nama.lower().replace(" ", ".") + "@alumni.umm.ac.id"
    aid = db.add_alumni(nama, prodi, 2022, kota, email)

    alumni = db.get_alumni_by_id(aid)
    result = pddikti_verifier.verify_alumni(dict(alumni))
    time.sleep(0.3)
    status = result["confidence"]
    umm_c = result["umm_results_count"]
    best = result.get("best_match")
    nim_info = f"NIM:{best['nim']}" if best else ""
    print(f"  #{aid} [{status}] {nama} | UMM:{umm_c} {nim_info}")

stats = db.get_dashboard_stats()
print(f"\nTotal Alumni now: {stats['total']}")
