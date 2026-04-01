"""
PDDIKTI Verifier module for Alumni Tracking System.
Uses the PDDIKTI public API to verify alumni data against the official
Indonesian Higher Education Database (PD-Dikti).

API base: https://api-pddikti.kemdiktisaintek.go.id
"""

import urllib.request
import urllib.parse
import json

PDDIKTI_BASE = "https://api-pddikti.kemdiktisaintek.go.id"
PDDIKTI_HEADERS = {
    "referer": "https://pddikti.kemdiktisaintek.go.id/",
    "origin": "https://pddikti.kemdiktisaintek.go.id",
    "accept": "application/json, text/plain, */*",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

# UMM identifiers on PDDIKTI
UMM_SINGKATAN = "UMM"
UMM_NAMA_RESMI = "UNIVERSITAS MUHAMMADIYAH MALANG"


def _fetch_json(url, timeout=10):
    """Fetch JSON from a URL with required headers. Returns dict/list or None."""
    try:
        req = urllib.request.Request(url, headers=PDDIKTI_HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except Exception:
        return None


def search_mahasiswa(nama):
    """
    Search for a student on PDDIKTI by name.
    Returns a list of matching records, each as a dict:
      { id, nama, nim, nama_pt, sinkatan_pt, nama_prodi }
    """
    encoded = urllib.parse.quote(nama)
    url = f"{PDDIKTI_BASE}/pencarian/mhs/{encoded}"
    result = _fetch_json(url)
    if isinstance(result, list):
        return result
    return []


def get_detail_mahasiswa(student_id):
    """
    Fetch detailed data for a student by their PDDIKTI ID.
    Returns a dict or None.
    """
    encoded = urllib.parse.quote(student_id, safe="")
    url = f"{PDDIKTI_BASE}/detail/mhs/{encoded}"
    return _fetch_json(url)


def is_umm_student(record):
    """Check if a PDDIKTI record belongs to UMM."""
    pt = (record.get("nama_pt") or "").upper()
    singkatan = (record.get("sinkatan_pt") or "").upper()
    return UMM_NAMA_RESMI in pt or UMM_SINGKATAN in singkatan


def verify_alumni(alumni_dict):
    """
    Verify an alumni against PDDIKTI data.

    Parameters:
        alumni_dict: dict with keys 'nama', 'prodi', 'tahun_lulus', 'kota'

    Returns a dict:
        {
          'found': bool,
          'umm_match': bool,
          'prodi_match': bool,
          'pddikti_results': list of matching PDDIKTI records,
          'best_match': dict or None,
          'confidence': 'Terverifikasi' | 'Kemungkinan' | 'Tidak Ditemukan'
        }
    """
    nama = alumni_dict.get("nama", "")
    prodi_input = (alumni_dict.get("prodi") or "").lower()

    all_results = search_mahasiswa(nama)

    if not all_results:
        return {
            "found": False,
            "umm_match": False,
            "prodi_match": False,
            "pddikti_results": [],
            "best_match": None,
            "confidence": "Tidak Ditemukan",
        }

    # Filter for UMM records
    umm_results = [r for r in all_results if is_umm_student(r)]

    best = None
    prodi_match = False

    if umm_results:
        # Try to find prodi match
        for r in umm_results:
            prodi_pddikti = (r.get("nama_prodi") or "").lower()
            # Match if any word in prodi appears in the pddikti prodi
            prodi_words = prodi_input.replace("teknik", "").strip().split()
            if any(w in prodi_pddikti for w in prodi_words if len(w) > 3):
                prodi_match = True
                best = r
                break
        if not best:
            best = umm_results[0]

        confidence = "Terverifikasi" if prodi_match else "Kemungkinan"
    else:
        # Not from UMM
        best = None
        confidence = "Tidak Ditemukan"

    return {
        "found": len(all_results) > 0,
        "umm_match": len(umm_results) > 0,
        "prodi_match": prodi_match,
        "pddikti_results": umm_results[:5],  # Return max 5 UMM results
        "all_results_count": len(all_results),
        "umm_results_count": len(umm_results),
        "best_match": best,
        "confidence": confidence,
    }
