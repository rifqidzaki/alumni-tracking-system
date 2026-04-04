import pddikti_verifier

test_cases = [
    {"nama": "Budi Santoso", "prodi": "Informatika", "tahun_lulus": 2022, "kota": "Malang"},
    {"nama": "Siti Nurhaliza", "prodi": "Sistem Informasi", "tahun_lulus": 2023, "kota": "Surabaya"},
    {"nama": "Andi Prasetyo", "prodi": "Teknik Informatika", "tahun_lulus": 2021, "kota": "Jakarta"},
]

for tc in test_cases:
    nama = tc["nama"]
    print(f"Testing: {nama}")
    result = pddikti_verifier.verify_alumni(tc)
    print(f"  Found: {result['found']} | Total results: {result['all_results_count']}")
    print(f"  UMM match: {result['umm_match']} | UMM count: {result['umm_results_count']}")
    print(f"  Confidence: {result['confidence']}")
    if result["best_match"]:
        bm = result["best_match"]
        print(f"  Best match: {bm['nama']} | NIM: {bm['nim']} | Prodi: {bm['nama_prodi']} | PT: {bm['sinkatan_pt']}")
    print()
