"""
Search PDDIKTI with specific full names to find real UMM students,
then seed them into the database and verify each one.
"""
import pddikti_verifier
import database as db
import time
import json

db.init_db()

# More specific full names common for UMM students
# Using combinations of common Indonesian names
search_queries = [
    "Muhammad Rizky UMM",
    "Ahmad Fauzi UMM",
    "Dewi Lestari UMM",
    "Siti Aisyah UMM",
    "Fajar Kurniawan UMM",
    "Putri Rahayu UMM",
    "Dimas Pratama UMM",
    "Andi Setiawan UMM",
    "Nur Hidayah UMM",
    "Yoga Pratama UMM",
    "Dian Permata UMM",
    "Eko Prasetyo UMM",
    "Wahyu Setiawan UMM",
    "Bayu Firmansyah UMM",
    "Rini Aprilia UMM",
    "Hendra Kusuma UMM",
    "Agus Setiawan UMM",
    "Rina Wulandari UMM",
    "Arif Rahman UMM",
    "Novi Andriani UMM",
    "Yusuf Maulana UMM",
    "Ratna Dewi UMM",
    "Indra Permana UMM",
    "Rizal Firmansyah UMM",
    "Fitri Handayani UMM",
    "Galih Prakosa UMM",
    "Nisa Amelia UMM",
    "Rahmat Hidayat UMM",
    "Laila Nurjanah UMM",
    "Irfan Hakim UMM",
]

umm_students = []
seen_nims = set()

print("=" * 70)
print("SEARCHING PDDIKTI FOR UMM STUDENTS (specific names)...")
print("=" * 70)

for query in search_queries:
    if len(umm_students) >= 21:
        break
    
    # search just by name part (remove "UMM")
    name_part = query.replace(" UMM", "")
    print(f"\nSearching: {name_part}...")
    results = pddikti_verifier.search_mahasiswa(name_part)
    time.sleep(0.3)

    for r in results:
        if len(umm_students) >= 21:
            break
        nim = r.get("nim", "")
        if nim in seen_nims:
            continue
        if pddikti_verifier.is_umm_student(r):
            seen_nims.add(nim)
            umm_students.append(r)
            prodi = r.get("nama_prodi", "Unknown")
            print(f"  FOUND UMM: {r['nama']} | NIM: {nim} | Prodi: {prodi}")

print(f"\n{'=' * 70}")
print(f"Total UMM students found: {len(umm_students)}")
print(f"{'=' * 70}\n")

# Map PDDIKTI prodi to system prodi
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

# Insert into database
print("INSERTING UMM ALUMNI INTO DATABASE...")
print("=" * 70)

added = []
for s in umm_students[:21]:
    nama = s["nama"].title()
    prodi = map_prodi(s.get("nama_prodi", "Informatika"))
    tahun_lulus = 2022
    kota = "Malang"
    email = nama.lower().replace(" ", ".") + "@alumni.umm.ac.id"

    alumni_id = db.add_alumni(nama, prodi, tahun_lulus, kota, email)
    added.append((alumni_id, nama))
    print(f"  #{alumni_id}: {nama} ({prodi})")

# Verify each one
print(f"\n{'=' * 70}")
print("VERIFYING ALL ALUMNI AGAINST PDDIKTI...")
print("=" * 70)

results_summary = []
for alumni_id, nama in added:
    alumni = db.get_alumni_by_id(alumni_id)
    if not alumni:
        continue
    result = pddikti_verifier.verify_alumni(dict(alumni))
    time.sleep(0.3)

    status = result["confidence"]
    umm_count = result["umm_results_count"]
    total = result["all_results_count"]
    best = result.get("best_match")
    best_info = ""
    if best:
        best_info = f" | Best: {best['nama']} NIM:{best['nim']} ({best['nama_prodi']})"

    emoji = {"Terverifikasi": "V", "Kemungkinan": "?", "Tidak Ditemukan": "X"}.get(status, "-")
    print(f"  [{emoji}] {status:20s} | {nama:30s} | PDDIKTI:{total} UMM:{umm_count}{best_info}")
    results_summary.append({
        "id": alumni_id,
        "nama": nama,
        "status": status,
        "umm_count": umm_count,
        "total_count": total,
    })

# Summary
print(f"\n{'=' * 70}")
print("VERIFICATION SUMMARY")
print("=" * 70)
v = sum(1 for r in results_summary if r["status"] == "Terverifikasi")
m = sum(1 for r in results_summary if r["status"] == "Kemungkinan")
n = sum(1 for r in results_summary if r["status"] == "Tidak Ditemukan")
print(f"  Terverifikasi    : {v}")
print(f"  Kemungkinan Cocok: {m}")
print(f"  Tidak Ditemukan  : {n}")
print(f"  Total Diverif.   : {len(results_summary)}")

stats = db.get_dashboard_stats()
print(f"\nDashboard Stats:")
print(f"  Total Alumni     : {stats['total']}")
