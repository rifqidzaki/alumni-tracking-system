import database as db
db.init_db()
st = db.get_dashboard_stats()
print("=== DASHBOARD STATS ===")
print(f"Total Alumni    : {st['total']}")
print(f"Sudah Dilacak   : {st['sudah_dilacak']}")
print(f"Perlu Verifikasi: {st['perlu_verifikasi']}")
print(f"Belum Dilacak   : {st['belum_dilacak']}")
print(f"Total Evidence  : {st['evidence_count']}")
print()
print("=== DAFTAR ALUMNI (terakhir 40) ===")
al, tot, _ = db.get_all_alumni(page=1, per_page=100)
rows = [dict(a) for a in al]
rows50 = rows[-40:]
for i, a in enumerate(rows50, 1):
    print(f"{i:>3}. {a['nama']:<35} {a['prodi']:<30} {a['status']}")
