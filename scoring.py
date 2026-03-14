"""
Scoring & Disambiguation module for Alumni Tracking System.
Handles query generation, confidence scoring, cross-validation, and classification.
"""

from difflib import SequenceMatcher


# ─── Query Generation ────────────────────────────────────────

def generate_queries(alumni):
    """
    Generate search queries based on alumni data.
    Returns a list of dicts with 'query' and 'source' keys.
    """
    nama = alumni['nama']
    prodi = alumni['prodi']
    kota = alumni['kota']
    tahun = alumni['tahun_lulus']

    # Abbreviation mapping
    prodi_abbrev = {
        'Informatika': 'IF',
        'Teknik Informatika': 'TI',
        'Sistem Informasi': 'SI',
        'Teknik Elektro': 'TE',
        'Teknik Mesin': 'TM',
        'Ilmu Komunikasi': 'Ilkom',
        'Manajemen': 'Manajemen',
        'Akuntansi': 'Akuntansi',
    }
    abbrev = prodi_abbrev.get(prodi, prodi[:2].upper())

    queries = [
        {
            'query': f'"{nama}" + "Universitas Muhammadiyah Malang"',
            'source': 'Google Search',
            'icon': 'bi-google'
        },
        {
            'query': f'"{nama}" + "{prodi}" + "UMM"',
            'source': 'Google Search',
            'icon': 'bi-google'
        },
        {
            'query': f'"{nama}" + site:linkedin.com',
            'source': 'LinkedIn',
            'icon': 'bi-linkedin'
        },
        {
            'query': f'"{nama}" + site:scholar.google.com',
            'source': 'Google Scholar',
            'icon': 'bi-mortarboard-fill'
        },
        {
            'query': f'"{nama}" + ORCID',
            'source': 'ORCID',
            'icon': 'bi-person-badge'
        },
        {
            'query': f'"{nama}" + site:researchgate.net',
            'source': 'ResearchGate',
            'icon': 'bi-journal-richtext'
        },
        {
            'query': f'"{nama}" + site:github.com',
            'source': 'GitHub',
            'icon': 'bi-github'
        },
        {
            'query': f'"{nama}" + site:kaggle.com',
            'source': 'Kaggle',
            'icon': 'bi-bar-chart-line'
        },
        {
            'query': f'"{nama}" + "{abbrev}" + "{kota}"',
            'source': 'General Search',
            'icon': 'bi-search'
        },
        {
            'query': f'"{nama}" + "Software Engineer" + "{kota}"',
            'source': 'Job Search',
            'icon': 'bi-briefcase'
        },
    ]
    return queries


# ─── Confidence Scoring ──────────────────────────────────────

def _name_similarity(name_a, name_b):
    """Calculate name similarity using SequenceMatcher (0-1)."""
    a = name_a.lower().strip()
    b = name_b.lower().strip()
    return SequenceMatcher(None, a, b).ratio()


def _affiliation_match(alumni, candidate):
    """
    Check if candidate affiliation matches alumni's university or city.
    Returns a score 0-1.
    """
    score = 0.0
    instansi = (candidate.get('instansi') or '').lower()
    lokasi = (candidate.get('lokasi') or '').lower()
    kota = alumni['kota'].lower()
    prodi = alumni['prodi'].lower()

    umm_keywords = ['umm', 'universitas muhammadiyah malang', 'muhammadiyah malang']
    for kw in umm_keywords:
        if kw in instansi:
            score += 0.5
            break

    if kota in lokasi or kota in instansi:
        score += 0.3

    if prodi in instansi or prodi in (candidate.get('bidang') or '').lower():
        score += 0.2

    return min(score, 1.0)


def _timeline_match(alumni, candidate):
    """
    Check if candidate's activity timeline is consistent with graduation year.
    Returns a score 0-1.
    """
    tahun_lulus = int(alumni['tahun_lulus'])
    tahun_aktivitas = candidate.get('tahun_aktivitas', '')

    if not tahun_aktivitas:
        return 0.3  # neutral if unknown

    try:
        years = [int(y.strip()) for y in str(tahun_aktivitas).replace('-', ',').split(',') if y.strip().isdigit()]
        if not years:
            return 0.3

        latest = max(years)
        earliest = min(years)

        # Activity should be around or after graduation
        if earliest >= tahun_lulus - 1 and latest >= tahun_lulus:
            return 1.0
        elif earliest >= tahun_lulus - 3:
            return 0.7
        else:
            return 0.3
    except (ValueError, TypeError):
        return 0.3


def _field_match(alumni, candidate):
    """
    Check if candidate's field matches alumni's program studi.
    Returns a score 0-1.
    """
    prodi = alumni['prodi'].lower()
    bidang = (candidate.get('bidang') or '').lower()
    jabatan = (candidate.get('jabatan') or '').lower()

    field_keywords = {
        'informatika': ['software', 'developer', 'programmer', 'engineer', 'data', 'it', 'web', 'mobile', 'computer', 'informatika', 'backend', 'frontend', 'fullstack', 'devops', 'machine learning', 'ai'],
        'sistem informasi': ['information system', 'analyst', 'erp', 'database', 'it', 'sistem informasi', 'business intelligence'],
        'teknik elektro': ['electrical', 'elektronik', 'iot', 'embedded', 'elektro', 'hardware'],
        'teknik mesin': ['mechanical', 'mesin', 'manufaktur', 'engineering'],
        'ilmu komunikasi': ['komunikasi', 'media', 'journalism', 'public relation', 'marketing'],
        'manajemen': ['manager', 'manajemen', 'business', 'finance', 'marketing'],
        'akuntansi': ['accountant', 'akuntansi', 'finance', 'audit', 'tax'],
    }

    best_score = 0.0
    for key, keywords in field_keywords.items():
        if key in prodi:
            for kw in keywords:
                if kw in bidang or kw in jabatan:
                    best_score = max(best_score, 1.0)
                    break
            break

    if best_score == 0.0:
        # Fallback to simple string matching
        if prodi in bidang or prodi in jabatan:
            best_score = 0.8

    return best_score


def calculate_confidence(alumni, candidate):
    """
    Calculate confidence score using weighted formula:
      Score = 0.4 * Name Match + 0.3 * Affiliation Match + 0.2 * Timeline Match + 0.1 * Field Match
    Returns a float 0-1.
    """
    name_score = _name_similarity(alumni['nama'], candidate.get('nama', ''))
    affiliation_score = _affiliation_match(alumni, candidate)
    timeline_score = _timeline_match(alumni, candidate)
    field_score = _field_match(alumni, candidate)

    score = (
        0.4 * name_score +
        0.3 * affiliation_score +
        0.2 * timeline_score +
        0.1 * field_score
    )
    return round(score, 2)


# ─── Cross Validation ────────────────────────────────────────

def cross_validate(candidates):
    """
    Cross-validate candidates found in multiple sources.
    Boosts score if same person found in multiple sources with consistent info.
    Lowers score if information is inconsistent.
    Returns updated list of candidates.
    """
    # Group by similar name
    name_groups = {}
    for c in candidates:
        matched = False
        for key in name_groups:
            if _name_similarity(c['nama'], key) > 0.8:
                name_groups[key].append(c)
                matched = True
                break
        if not matched:
            name_groups[c['nama']] = [c]

    for name, group in name_groups.items():
        if len(group) > 1:
            # Found in multiple sources
            sources = set(c.get('sumber', '') for c in group)

            # Check consistency of instansi and jabatan
            instansi_set = set(c.get('instansi', '') for c in group if c.get('instansi'))
            jabatan_set = set(c.get('jabatan', '') for c in group if c.get('jabatan'))

            if len(instansi_set) <= 1 and len(jabatan_set) <= 1:
                # Consistent info → boost
                boost = min(0.15, 0.05 * len(sources))
                for c in group:
                    c['confidence_score'] = min(1.0, round(c['confidence_score'] + boost, 2))
                    c['cross_validated'] = True
                    c['cross_sources'] = list(sources)
            else:
                # Inconsistent → reduce
                for c in group:
                    c['confidence_score'] = max(0.0, round(c['confidence_score'] - 0.05, 2))
                    c['cross_validated'] = True
                    c['cross_sources'] = list(sources)
                    c['inconsistent'] = True
        else:
            for c in group:
                c['cross_validated'] = False
                c['cross_sources'] = []

    return candidates


# ─── Classification ──────────────────────────────────────────

def classify(score):
    """
    Classify a candidate based on confidence score.
      ≥ 0.75 → Strong Match
      0.50 – 0.74 → Need Verification
      < 0.50 → Not Match
    """
    if score >= 0.75:
        return 'strong_match'
    elif score >= 0.50:
        return 'need_verification'
    else:
        return 'not_match'


def classify_label(status):
    """Return human-readable label for a status."""
    labels = {
        'strong_match': 'Strong Match',
        'need_verification': 'Need Verification',
        'not_match': 'Not Match'
    }
    return labels.get(status, status)


def classify_badge(status):
    """Return Bootstrap badge class for a status."""
    badges = {
        'strong_match': 'bg-success',
        'need_verification': 'bg-warning text-dark',
        'not_match': 'bg-danger'
    }
    return badges.get(status, 'bg-secondary')
