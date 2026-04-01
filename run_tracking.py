"""
Run full tracking pipeline for 12 alumni:
  1. Simulate search (generate candidates with confidence scores)
  2. Save the best candidate as evidence
  3. Verify against PDDIKTI
"""
import database as db
import scoring
import search_simulator
import pddikti_verifier
import time

db.init_db()

# Get 12 alumni that haven't been tracked yet
all_alumni, total, _ = db.get_all_alumni(page=1, per_page=50)
untracked = [dict(a) for a in all_alumni if dict(a)["status"] == "belum_dilacak"][:12]

print("=" * 80)
print(f"PELACAKAN & VALIDASI 12 ALUMNI")
print("=" * 80)

results = []

for i, alumni in enumerate(untracked, 1):
    alumni_id = alumni["id"]
    nama = alumni["nama"]
    prodi = alumni["prodi"]

    print(f"\n--- [{i}/12] {nama} ({prodi}) ---")

    # Step 1: Simulate search
    candidates = search_simulator.simulate_search(alumni)
    for c in candidates:
        c["confidence_score"] = scoring.calculate_confidence(alumni, c)
    candidates = scoring.cross_validate(candidates)
    for c in candidates:
        c["status"] = scoring.classify(c["confidence_score"])
    candidates.sort(key=lambda x: x["confidence_score"], reverse=True)
    db.save_candidates(alumni_id, candidates)

    best = candidates[0]
    print(f"  Pencarian: {len(candidates)} kandidat ditemukan")
    print(f"  Best match: {best['nama']} | Score: {best['confidence_score']} | {best['sumber']}")

    # Step 2: Save evidence for best candidate
    db.save_evidence(
        alumni_id=alumni_id,
        candidate_id=1,
        nama_alumni=best["nama"],
        instansi=best.get("instansi", ""),
        jabatan=best.get("jabatan", ""),
        sumber=best.get("sumber", ""),
        link=best.get("link", ""),
        confidence_score=best["confidence_score"],
    )
    status_label = scoring.classify_label(best["status"])
    print(f"  Evidence saved: {status_label} (score: {best['confidence_score']})")

    # Step 3: PDDIKTI verification
    pddikti_result = pddikti_verifier.verify_alumni(alumni)
    time.sleep(0.3)
    pddikti_status = pddikti_result["confidence"]
    umm_count = pddikti_result["umm_results_count"]
    pddikti_best = pddikti_result.get("best_match")
    nim = pddikti_best["nim"] if pddikti_best else "-"
    print(f"  PDDIKTI: {pddikti_status} | UMM matches: {umm_count} | NIM: {nim}")

    results.append({
        "no": i,
        "nama": nama,
        "prodi": prodi,
        "candidates": len(candidates),
        "best_score": best["confidence_score"],
        "best_status": status_label,
        "evidence_source": best["sumber"],
        "pddikti_status": pddikti_status,
        "pddikti_umm": umm_count,
        "pddikti_nim": nim,
    })

# Summary table
print(f"\n{'=' * 80}")
print("RINGKASAN PELACAKAN & VALIDASI")
print("=" * 80)
print(f"{'No':>3} | {'Nama':<28} | {'Score':>5} | {'Status Cari':<18} | {'PDDIKTI':<17} | {'NIM':<20}")
print("-" * 110)
for r in results:
    print(f"{r['no']:>3} | {r['nama']:<28} | {r['best_score']:>5} | {r['best_status']:<18} | {r['pddikti_status']:<17} | {r['pddikti_nim']:<20}")

print(f"\n{'=' * 80}")
stats = db.get_dashboard_stats()
print(f"Dashboard Stats:")
print(f"  Total Alumni       : {stats['total']}")
print(f"  Sudah Dilacak      : {stats['sudah_dilacak']}")
print(f"  Perlu Verifikasi   : {stats['perlu_verifikasi']}")
print(f"  Belum Dilacak      : {stats['belum_dilacak']}")
print(f"  Total Evidence     : {stats['evidence_count']}")
