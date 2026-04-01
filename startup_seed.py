"""
Startup seed data for Alumni Tracking System.
Called once when the database is empty (fresh deploy).
Contains 40 real/realistic UMM alumni records.
"""

import database as db
import scoring
import search_simulator


ALUMNI_DATA = [
    # (nama, prodi, tahun_lulus, kota, email) - 19 real names from PDDIKTI UMM
    ("Bayu Firmansyah",              "Informatika",                       2021, "Malang",    "bayu.firmansyah@alumni.umm.ac.id"),
    ("Wahyu Setiawan",               "Fisioterapi",                       2020, "Malang",    "wahyu.setiawan@alumni.umm.ac.id"),
    ("Irfan Hakim",                  "Teknik Elektro",                    2019, "Malang",    "irfan.hakim@alumni.umm.ac.id"),
    ("Dinda Permatasari",            "Farmasi",                           2023, "Malang",    "dinda.permatasari@alumni.umm.ac.id"),
    ("Rofiq Hidayat",                "Hukum",                             2022, "Malang",    "rofiq.hidayat@alumni.umm.ac.id"),
    ("Lailatul Fitriyah",            "Kedokteran",                        2018, "Malang",    "lailatul.fitriyah@alumni.umm.ac.id"),
    ("Alfian Nur",                   "Agribisnis",                        2016, "Malang",    "alfian.nur@alumni.umm.ac.id"),
    ("Lutfi Hakim",                  "Akuntansi",                         2000, "Malang",    "lutfi.hakim@alumni.umm.ac.id"),
    ("Novi Andriani",                "Sosiologi",                         2019, "Malang",    "novi.andriani@alumni.umm.ac.id"),
    ("Rizal Firmansyah",             "Manajemen",                         2024, "Malang",    "rizal.firmansyah@alumni.umm.ac.id"),
    ("Nisa Amelia",                  "Ilmu Komunikasi",                   2010, "Malang",    "nisa.amelia@alumni.umm.ac.id"),
    ("Zulfikar Ahmad",               "Hukum",                             2020, "Malang",    "zulfikar.ahmad@alumni.umm.ac.id"),
    ("Zulfikar Ahmad Wildan",        "Psikologi",                         2020, "Malang",    "zulfikar.ahmad.wildan@alumni.umm.ac.id"),
    ("Anis Sulistyowati",            "Agroteknologi",                     2002, "Malang",    "anis.sulistyowati@alumni.umm.ac.id"),
    ("Mohammad Lutfi Hakim",         "Manajemen",                         2014, "Malang",    "mohammad.lutfi.hakim@alumni.umm.ac.id"),
    ("Rini Aprilia Agustin",         "Pendidikan Bahasa Indonesia",       2024, "Malang",    "rini.aprilia.agustin@alumni.umm.ac.id"),
    ("Hendra Kusuma",                "Hukum",                             2004, "Malang",    "hendra.kusuma@alumni.umm.ac.id"),
    ("Muhammad Irfan Hakim",         "Sosiologi",                         2022, "Malang",    "muhammad.irfan.hakim@alumni.umm.ac.id"),
    ("Anggun Dinda Permatasari",     "Akuntansi",                         2025, "Malang",    "anggun.dinda.permatasari@alumni.umm.ac.id"),
    # 21 realistic UMM alumni
    ("Ahmad Rizky Pratama",          "Informatika",                       2021, "Malang",    "ahmad.rizky@alumni.umm.ac.id"),
    ("Siti Nurhaliza",               "Sistem Informasi",                  2023, "Surabaya",  "siti.nurhaliza@alumni.umm.ac.id"),
    ("Andi Prasetyo",                "Teknik Informatika",                2021, "Jakarta",   "andi.prasetyo@alumni.umm.ac.id"),
    ("Dewi Lestari",                 "Informatika",                       2022, "Bandung",   "dewi.lestari@alumni.umm.ac.id"),
    ("Rizky Ramadhan",               "Teknik Elektro",                    2020, "Malang",    "rizky.ramadhan@alumni.umm.ac.id"),
    ("Fajar Maulana",                "Teknik Mesin",                      2023, "Surabaya",  "fajar.maulana@alumni.umm.ac.id"),
    ("Nadia Putri",                  "Ilmu Komunikasi",                   2022, "Yogyakarta","nadia.putri@alumni.umm.ac.id"),
    ("Muhammad Faisal",              "Manajemen",                         2021, "Malang",    "muhammad.faisal@alumni.umm.ac.id"),
    ("Ayu Kartika",                  "Akuntansi",                         2023, "Malang",    "ayu.kartika@alumni.umm.ac.id"),
    ("Budi Santoso",                 "Informatika",                       2022, "Malang",    "budi.santoso@alumni.umm.ac.id"),
    ("Hendra Wijaya",                "Teknik Informatika",                2020, "Jakarta",   "hendra.wijaya@alumni.umm.ac.id"),
    ("Rina Agustina",                "Sistem Informasi",                  2021, "Semarang",  "rina.agustina@alumni.umm.ac.id"),
    ("Dimas Arya Putra",             "Informatika",                       2022, "Malang",    "dimas.arya@alumni.umm.ac.id"),
    ("Laras Sekar Arum",             "Ilmu Komunikasi",                   2023, "Malang",    "laras.sekar@alumni.umm.ac.id"),
    ("Yoga Prakoso",                 "Teknik Mesin",                      2020, "Surabaya",  "yoga.prakoso@alumni.umm.ac.id"),
    ("Citra Dewi Maharani",          "Akuntansi",                         2022, "Malang",    "citra.dewi@alumni.umm.ac.id"),
    ("Fandi Ahmad",                  "Manajemen",                         2021, "Malang",    "fandi.ahmad@alumni.umm.ac.id"),
    ("Rahma Aulia",                  "Informatika",                       2023, "Bandung",   "rahma.aulia@alumni.umm.ac.id"),
    ("Eko Budi Santoso",             "Teknik Elektro",                    2022, "Malang",    "eko.budi@alumni.umm.ac.id"),
    ("Nadya Safira",                 "Sistem Informasi",                  2021, "Malang",    "nadya.safira@alumni.umm.ac.id"),
    ("Galih Wicaksono",              "Teknik Informatika",                2022, "Malang",    "galih.wicaksono@alumni.umm.ac.id"),
]


def seed_if_empty():
    """Seed database with 40 alumni and run tracking if DB is empty."""
    total = db.get_dashboard_stats()["total"]
    if total > 0:
        return  # Already seeded

    print("[seed] Database empty — seeding 40 alumni...")
    ids = []
    for nama, prodi, tahun, kota, email in ALUMNI_DATA:
        aid = db.add_alumni(nama, prodi, tahun, kota, email)
        ids.append(aid)

    # Run tracking simulation for all alumni
    for aid in ids:
        alumni = dict(db.get_alumni_by_id(aid))
        try:
            candidates = search_simulator.simulate_search(alumni)
            for c in candidates:
                c["confidence_score"] = scoring.calculate_confidence(alumni, c)
            candidates = scoring.cross_validate(candidates)
            for c in candidates:
                c["status"] = scoring.classify(c["confidence_score"])
            candidates.sort(key=lambda x: x["confidence_score"], reverse=True)
            db.save_candidates(aid, candidates)

            best = candidates[0]
            db.save_evidence(
                alumni_id=aid,
                candidate_id=1,
                nama_alumni=best["nama"],
                instansi=best.get("instansi", ""),
                jabatan=best.get("jabatan", ""),
                sumber=best.get("sumber", ""),
                link=best.get("link", ""),
                confidence_score=best["confidence_score"],
            )
        except Exception as e:
            print(f"[seed] Warning: tracking failed for {alumni['nama']}: {e}")

    print(f"[seed] Done! {len(ids)} alumni seeded with tracking evidence.")
