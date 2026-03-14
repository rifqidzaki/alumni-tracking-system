"""Seed 11 alumni records into the database."""
import database as db

db.init_db()

alumni_data = [
    ("Budi Santoso", "Informatika", 2022, "Malang", "budi.santoso@gmail.com"),
    ("Siti Nurhaliza", "Sistem Informasi", 2023, "Surabaya", "siti.nurhaliza@gmail.com"),
    ("Andi Prasetyo", "Teknik Informatika", 2021, "Jakarta", "andi.prasetyo@gmail.com"),
    ("Dewi Lestari", "Informatika", 2022, "Bandung", "dewi.lestari@gmail.com"),
    ("Rizky Ramadhan", "Teknik Elektro", 2020, "Malang", "rizky.ramadhan@gmail.com"),
    ("Fajar Maulana", "Informatika", 2023, "Yogyakarta", "fajar.maulana@gmail.com"),
    ("Nadia Putri", "Manajemen", 2021, "Semarang", "nadia.putri@gmail.com"),
    ("Hendra Wijaya", "Teknik Mesin", 2020, "Malang", "hendra.wijaya@gmail.com"),
    ("Ayu Kartika", "Ilmu Komunikasi", 2022, "Jakarta", "ayu.kartika@gmail.com"),
    ("Muhammad Faisal", "Informatika", 2023, "Malang", "mfaisal@gmail.com"),
    ("Rina Agustina", "Akuntansi", 2021, "Surabaya", "rina.agustina@gmail.com"),
]

for nama, prodi, tahun, kota, email in alumni_data:
    db.add_alumni(nama, prodi, tahun, kota, email)
    print(f"Added: {nama}")

stats = db.get_dashboard_stats()
print(f"\nTotal alumni sekarang: {stats['total']}")
