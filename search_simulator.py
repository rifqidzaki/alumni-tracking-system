"""
Search Simulator module for Alumni Tracking System.
Generates realistic simulated search results for alumni tracking.
Since we cannot perform real web scraping, this module produces
sample candidate data from various public sources.
"""

import random
import hashlib


def _hash_seed(text):
    """Generate a deterministic seed from text for consistent results."""
    return int(hashlib.md5(text.encode()).hexdigest()[:8], 16)


# ─── Data Pools ───────────────────────────────────────────────

COMPANIES = [
    'PT Telkom Indonesia', 'Tokopedia', 'Gojek', 'Traveloka', 'Bukalapak',
    'Bank BCA', 'Bank Mandiri', 'Astra International', 'Pertamina',
    'Samsung R&D Indonesia', 'Google Indonesia', 'Microsoft Indonesia',
    'Shopee Indonesia', 'Blibli.com', 'Dana Indonesia', 'OVO',
    'PT Infomedia Nusantara', 'Tiket.com', 'Ruangguru', 'Zenius',
    'Universitas Muhammadiyah Malang', 'Universitas Brawijaya',
    'Institut Teknologi Sepuluh Nopember', 'Universitas Indonesia',
    'Universitas Gadjah Mada', 'Universitas Airlangga',
]

POSITIONS_IT = [
    'Software Engineer', 'Backend Developer', 'Frontend Developer',
    'Full Stack Developer', 'Data Scientist', 'Data Analyst',
    'Machine Learning Engineer', 'DevOps Engineer', 'QA Engineer',
    'Mobile Developer', 'Product Manager', 'IT Consultant',
    'System Administrator', 'Network Engineer', 'UI/UX Designer',
    'Web Developer', 'Cloud Engineer', 'Security Analyst',
]

POSITIONS_GENERAL = [
    'Staff Administrasi', 'Marketing Manager', 'HRD Manager',
    'Business Analyst', 'Project Manager', 'Consultant',
    'Research Assistant', 'Lecturer', 'Dosen', 'Asisten Peneliti',
    'Akuntan', 'Finance Analyst', 'Public Relations',
]

CITIES = [
    'Malang', 'Surabaya', 'Jakarta', 'Bandung', 'Yogyakarta',
    'Semarang', 'Bali', 'Makassar', 'Medan', 'Palembang',
    'Bogor', 'Tangerang', 'Bekasi', 'Depok',
]

FIELDS_IT = [
    'Software Development', 'Web Development', 'Data Science',
    'Machine Learning', 'Computer Vision', 'Natural Language Processing',
    'Cloud Computing', 'Cybersecurity', 'IoT', 'Mobile Development',
    'Artificial Intelligence', 'Information Systems',
]

FIELDS_GENERAL = [
    'Business Management', 'Marketing', 'Finance', 'Accounting',
    'Human Resources', 'Education', 'Research', 'Communication',
    'Electrical Engineering', 'Mechanical Engineering',
]

SOURCES = [
    {'name': 'LinkedIn', 'base_url': 'https://linkedin.com/in/', 'icon': 'bi-linkedin'},
    {'name': 'Google Scholar', 'base_url': 'https://scholar.google.com/citations?user=', 'icon': 'bi-mortarboard-fill'},
    {'name': 'ResearchGate', 'base_url': 'https://researchgate.net/profile/', 'icon': 'bi-journal-richtext'},
    {'name': 'GitHub', 'base_url': 'https://github.com/', 'icon': 'bi-github'},
    {'name': 'ORCID', 'base_url': 'https://orcid.org/0000-000', 'icon': 'bi-person-badge'},
    {'name': 'Kaggle', 'base_url': 'https://kaggle.com/', 'icon': 'bi-bar-chart-line'},
    {'name': 'Website Perusahaan', 'base_url': 'https://company.co.id/team/', 'icon': 'bi-building'},
    {'name': 'Berita Online', 'base_url': 'https://news.example.com/article/', 'icon': 'bi-newspaper'},
]


# ─── Name Variations ─────────────────────────────────────────

def _generate_name_variations(nama):
    """Generate plausible name variations for search results."""
    parts = nama.strip().split()
    variations = [nama]  # exact match

    if len(parts) >= 2:
        # First name + Last name
        variations.append(f"{parts[0]} {parts[-1]}")
        # Initials
        initials = '. '.join(p[0].upper() for p in parts[:-1]) + '. ' + parts[-1]
        variations.append(initials)

    # Add some different people with same first name
    if len(parts) >= 1:
        first = parts[0]
        filler_lastnames = ['Pratama', 'Wijaya', 'Santoso', 'Kusuma', 'Saputra',
                            'Hidayat', 'Rahman', 'Nugroho', 'Setiawan', 'Firmansyah']
        random.seed(_hash_seed(nama))
        chosen = random.sample(filler_lastnames, min(3, len(filler_lastnames)))
        for ln in chosen:
            if ln.lower() not in nama.lower():
                variations.append(f"{first} {ln}")

    return variations


# ─── Simulate Search Results ─────────────────────────────────

def simulate_search(alumni):
    """
    Simulate search results for an alumni.
    Returns a list of candidate dicts.
    """
    nama = alumni['nama']
    prodi = alumni['prodi']
    kota = alumni['kota']
    tahun_lulus = int(alumni['tahun_lulus'])

    random.seed(_hash_seed(nama + prodi))
    candidates = []

    name_variations = _generate_name_variations(nama)
    is_it_prodi = any(kw in prodi.lower() for kw in ['informatika', 'sistem informasi', 'teknik komputer', 'ilmu komputer'])

    positions = POSITIONS_IT if is_it_prodi else POSITIONS_GENERAL
    fields = FIELDS_IT if is_it_prodi else FIELDS_GENERAL

    # ── Candidate 1: Strong match (same name, correct affiliation) ──
    source1 = random.choice(SOURCES[:4])  # LinkedIn, Scholar, RG, GitHub
    slug = nama.lower().replace(' ', '-')
    candidates.append({
        'nama': nama,
        'instansi': random.choice(['Universitas Muhammadiyah Malang', 'UMM',
                                    random.choice(COMPANIES[:6])]),
        'jabatan': random.choice(positions),
        'lokasi': kota,
        'bidang': random.choice(fields),
        'tahun_aktivitas': f"{tahun_lulus}-{tahun_lulus + random.randint(1, 5)}",
        'sumber': source1['name'],
        'link': f"{source1['base_url']}{slug}",
    })

    # ── Candidate 2: Same person, different source (for cross-validation) ──
    remaining_sources = [s for s in SOURCES if s['name'] != source1['name']]
    source2 = random.choice(remaining_sources[:4])
    candidates.append({
        'nama': nama,
        'instansi': candidates[0]['instansi'],  # consistent
        'jabatan': candidates[0]['jabatan'],
        'lokasi': kota,
        'bidang': candidates[0]['bidang'],
        'tahun_aktivitas': f"{tahun_lulus + 1}-{tahun_lulus + random.randint(2, 6)}",
        'sumber': source2['name'],
        'link': f"{source2['base_url']}{slug}",
    })

    # ── Candidate 3: Partial match (same name, different city) ──
    other_city = random.choice([c for c in CITIES if c != kota])
    source3 = random.choice(remaining_sources)
    candidates.append({
        'nama': nama,
        'instansi': random.choice(COMPANIES[6:]),
        'jabatan': random.choice(positions),
        'lokasi': other_city,
        'bidang': random.choice(fields),
        'tahun_aktivitas': f"{tahun_lulus - 2}-{tahun_lulus + random.randint(0, 3)}",
        'sumber': source3['name'],
        'link': f"{source3['base_url']}{slug}-2",
    })

    # ── Candidates 4-6: Different people with similar names ──
    for i, var_name in enumerate(name_variations[1:4], start=4):
        src = random.choice(SOURCES)
        var_slug = var_name.lower().replace(' ', '-').replace('.', '')
        other_city2 = random.choice(CITIES)
        candidates.append({
            'nama': var_name,
            'instansi': random.choice(COMPANIES),
            'jabatan': random.choice(POSITIONS_IT + POSITIONS_GENERAL),
            'lokasi': other_city2,
            'bidang': random.choice(FIELDS_IT + FIELDS_GENERAL),
            'tahun_aktivitas': f"{random.randint(2015, 2024)}-{random.randint(2024, 2026)}",
            'sumber': src['name'],
            'link': f"{src['base_url']}{var_slug}",
        })

    # ── Candidate 7: Scholar/academic match ──
    scholar_source = next((s for s in SOURCES if s['name'] == 'Google Scholar'), SOURCES[1])
    candidates.append({
        'nama': nama,
        'instansi': 'Universitas Muhammadiyah Malang',
        'jabatan': 'Researcher' if is_it_prodi else 'Lecturer',
        'lokasi': 'Malang',
        'bidang': random.choice(fields),
        'tahun_aktivitas': f"{tahun_lulus}-{tahun_lulus + random.randint(1, 4)}",
        'sumber': scholar_source['name'],
        'link': f"{scholar_source['base_url']}{slug}-scholar",
    })

    return candidates
