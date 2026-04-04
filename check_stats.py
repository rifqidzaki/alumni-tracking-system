import database as db
db.init_db()
s = db.get_dashboard_stats()
print("Total Alumni:", s["total"])
print("Fakultas:", len(s.get("fakultas_stats", [])))
for f in s.get("fakultas_stats", []):
    print(f"  {f['fakultas']}: {f['jumlah']}")
