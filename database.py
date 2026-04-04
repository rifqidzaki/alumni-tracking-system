"""
Database module for Alumni Tracking System.
Handles SQLite database initialization and CRUD operations.
Extended with: users table, alumni contact/employment fields.
"""

import sqlite3
import os
import hashlib
from datetime import datetime

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')


def get_db():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize the database with required tables."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nama_lengkap TEXT,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alumni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            nim TEXT,
            tahun_masuk TEXT,
            tanggal_lulus TEXT,
            fakultas TEXT,
            prodi TEXT NOT NULL,
            tahun_lulus INTEGER NOT NULL,
            kota TEXT NOT NULL,
            email TEXT,
            no_hp TEXT,
            linkedin TEXT,
            instagram TEXT,
            facebook TEXT,
            tiktok TEXT,
            tempat_bekerja TEXT,
            alamat_bekerja TEXT,
            posisi TEXT,
            jenis_pekerjaan TEXT,
            sosmed_perusahaan TEXT,
            status TEXT DEFAULT 'belum_dilacak',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS search_candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumni_id INTEGER NOT NULL,
            nama TEXT NOT NULL,
            instansi TEXT,
            jabatan TEXT,
            lokasi TEXT,
            bidang TEXT,
            tahun_aktivitas TEXT,
            sumber TEXT,
            link TEXT,
            confidence_score REAL DEFAULT 0.0,
            status TEXT DEFAULT 'not_match',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (alumni_id) REFERENCES alumni(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS tracking_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumni_id INTEGER NOT NULL,
            candidate_id INTEGER,
            nama_alumni TEXT NOT NULL,
            instansi TEXT,
            jabatan TEXT,
            sumber TEXT,
            link TEXT,
            confidence_score REAL DEFAULT 0.0,
            tanggal_ditemukan TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (alumni_id) REFERENCES alumni(id) ON DELETE CASCADE
        );
    ''')

    # Add new columns to alumni if they don't exist (for migration)
    _migrate_alumni_table(cursor)

    conn.commit()
    conn.close()

    # Create default admin user
    create_default_user()


def _migrate_alumni_table(cursor):
    """Add new columns if they don't exist (for existing databases)."""
    existing = {row[1] for row in cursor.execute("PRAGMA table_info(alumni)").fetchall()}
    new_columns = {
        'nim': 'TEXT', 'tahun_masuk': 'TEXT', 'tanggal_lulus': 'TEXT',
        'fakultas': 'TEXT', 'no_hp': 'TEXT', 'linkedin': 'TEXT',
        'instagram': 'TEXT', 'facebook': 'TEXT', 'tiktok': 'TEXT',
        'tempat_bekerja': 'TEXT', 'alamat_bekerja': 'TEXT',
        'posisi': 'TEXT', 'jenis_pekerjaan': 'TEXT', 'sosmed_perusahaan': 'TEXT',
    }
    for col, typ in new_columns.items():
        if col not in existing:
            cursor.execute(f'ALTER TABLE alumni ADD COLUMN {col} {typ}')


# ─── User Auth ────────────────────────────────────────────────

def hash_password(password):
    """Hash password with SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def create_default_user():
    """Create default admin user if no users exist."""
    conn = get_db()
    count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if count == 0:
        conn.execute(
            'INSERT INTO users (username, password_hash, nama_lengkap, role) VALUES (?, ?, ?, ?)',
            ('admin', hash_password('ATS@umm2026'), 'Administrator', 'admin')
        )
        conn.commit()
    conn.close()


def verify_user(username, password):
    """Verify user credentials. Returns user row or None."""
    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? AND password_hash = ?',
        (username, hash_password(password))
    ).fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    """Get user by ID."""
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user


# ─── Alumni CRUD ──────────────────────────────────────────────

def add_alumni(nama, prodi, tahun_lulus, kota, email=None, nim=None,
               tahun_masuk=None, tanggal_lulus=None, fakultas=None):
    """Insert a new alumni record."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alumni (nama, nim, tahun_masuk, tanggal_lulus, fakultas, prodi, tahun_lulus, kota, email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nama, nim, tahun_masuk, tanggal_lulus, fakultas, prodi, tahun_lulus, kota, email))
    conn.commit()
    alumni_id = cursor.lastrowid
    conn.close()
    return alumni_id


def add_alumni_bulk(records):
    """Bulk insert alumni records. Each record is a tuple:
    (nama, nim, tahun_masuk, tanggal_lulus, fakultas, prodi, tahun_lulus, kota)
    Returns count inserted.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO alumni (nama, nim, tahun_masuk, tanggal_lulus, fakultas, prodi, tahun_lulus, kota)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', records)
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count


def get_all_alumni(search=None, prodi_filter=None, tahun_filter=None,
                   fakultas_filter=None, page=1, per_page=10):
    """Get all alumni with optional filtering and pagination."""
    conn = get_db()
    query = 'SELECT * FROM alumni WHERE 1=1'
    params = []

    if search:
        query += ' AND (nama LIKE ? OR kota LIKE ? OR email LIKE ? OR nim LIKE ?)'
        like = f'%{search}%'
        params.extend([like, like, like, like])

    if prodi_filter:
        query += ' AND prodi = ?'
        params.append(prodi_filter)

    if tahun_filter:
        query += ' AND tahun_lulus = ?'
        params.append(int(tahun_filter))

    if fakultas_filter:
        query += ' AND fakultas = ?'
        params.append(fakultas_filter)

    # Count total
    count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
    total = conn.execute(count_query, params).fetchone()[0]

    # Paginate
    query += ' ORDER BY id ASC LIMIT ? OFFSET ?'
    params.extend([per_page, (page - 1) * per_page])

    alumni_list = conn.execute(query, params).fetchall()
    conn.close()

    total_pages = max(1, (total + per_page - 1) // per_page)
    return alumni_list, total, total_pages


def get_alumni_by_id(alumni_id):
    """Get a single alumni by ID."""
    conn = get_db()
    alumni = conn.execute('SELECT * FROM alumni WHERE id = ?', (alumni_id,)).fetchone()
    conn.close()
    return alumni


def update_alumni_status(alumni_id, status):
    """Update the tracking status of an alumni."""
    conn = get_db()
    conn.execute('UPDATE alumni SET status = ? WHERE id = ?', (status, alumni_id))
    conn.commit()
    conn.close()


def update_alumni_contact(alumni_id, data):
    """Update alumni contact and employment information."""
    conn = get_db()
    conn.execute('''
        UPDATE alumni SET
            email = ?, no_hp = ?, linkedin = ?, instagram = ?,
            facebook = ?, tiktok = ?, tempat_bekerja = ?,
            alamat_bekerja = ?, posisi = ?, jenis_pekerjaan = ?,
            sosmed_perusahaan = ?
        WHERE id = ?
    ''', (
        data.get('email'), data.get('no_hp'), data.get('linkedin'),
        data.get('instagram'), data.get('facebook'), data.get('tiktok'),
        data.get('tempat_bekerja'), data.get('alamat_bekerja'),
        data.get('posisi'), data.get('jenis_pekerjaan'),
        data.get('sosmed_perusahaan'), alumni_id
    ))
    conn.commit()
    conn.close()


def get_all_prodi():
    """Get distinct list of program studi."""
    conn = get_db()
    rows = conn.execute('SELECT DISTINCT prodi FROM alumni ORDER BY prodi').fetchall()
    conn.close()
    return [r['prodi'] for r in rows]


def get_all_tahun():
    """Get distinct list of graduation years."""
    conn = get_db()
    rows = conn.execute('SELECT DISTINCT tahun_lulus FROM alumni ORDER BY tahun_lulus DESC').fetchall()
    conn.close()
    return [r['tahun_lulus'] for r in rows]


def get_all_fakultas():
    """Get distinct list of fakultas."""
    conn = get_db()
    rows = conn.execute('SELECT DISTINCT fakultas FROM alumni WHERE fakultas IS NOT NULL ORDER BY fakultas').fetchall()
    conn.close()
    return [r['fakultas'] for r in rows]


# ─── Search Candidates CRUD ──────────────────────────────────

def save_candidates(alumni_id, candidates):
    """Save a list of search candidate dicts for an alumni."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM search_candidates WHERE alumni_id = ?', (alumni_id,))
    for c in candidates:
        cursor.execute('''
            INSERT INTO search_candidates
            (alumni_id, nama, instansi, jabatan, lokasi, bidang, tahun_aktivitas, sumber, link, confidence_score, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alumni_id,
            c.get('nama', ''), c.get('instansi', ''), c.get('jabatan', ''),
            c.get('lokasi', ''), c.get('bidang', ''), c.get('tahun_aktivitas', ''),
            c.get('sumber', ''), c.get('link', ''),
            c.get('confidence_score', 0.0), c.get('status', 'not_match')
        ))
    conn.commit()
    conn.close()


def get_candidates_by_alumni(alumni_id):
    """Get all search candidates for an alumni."""
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM search_candidates WHERE alumni_id = ? ORDER BY confidence_score DESC',
        (alumni_id,)
    ).fetchall()
    conn.close()
    return rows


# ─── Tracking Evidence CRUD ──────────────────────────────────

def save_evidence(alumni_id, candidate_id, nama_alumni, instansi, jabatan, sumber, link, confidence_score):
    """Save a tracking evidence record."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tracking_evidence
        (alumni_id, candidate_id, nama_alumni, instansi, jabatan, sumber, link, confidence_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (alumni_id, candidate_id, nama_alumni, instansi, jabatan, sumber, link, confidence_score))
    conn.commit()

    if confidence_score >= 0.75:
        update_alumni_status(alumni_id, 'sudah_dilacak')
    else:
        update_alumni_status(alumni_id, 'perlu_verifikasi')

    conn.close()


def get_all_evidence(page=1, per_page=10):
    """Get all tracking evidence with pagination."""
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM tracking_evidence').fetchone()[0]
    rows = conn.execute(
        'SELECT * FROM tracking_evidence ORDER BY tanggal_ditemukan DESC LIMIT ? OFFSET ?',
        (per_page, (page - 1) * per_page)
    ).fetchall()
    conn.close()
    total_pages = max(1, (total + per_page - 1) // per_page)
    return rows, total, total_pages


# ─── Dashboard Stats ─────────────────────────────────────────

def get_dashboard_stats():
    """Get statistics for the dashboard."""
    conn = get_db()

    total = conn.execute('SELECT COUNT(*) FROM alumni').fetchone()[0]
    sudah = conn.execute("SELECT COUNT(*) FROM alumni WHERE status = 'sudah_dilacak'").fetchone()[0]
    belum = conn.execute("SELECT COUNT(*) FROM alumni WHERE status = 'belum_dilacak'").fetchone()[0]
    verifikasi = conn.execute("SELECT COUNT(*) FROM alumni WHERE status = 'perlu_verifikasi'").fetchone()[0]
    evidence_count = conn.execute('SELECT COUNT(*) FROM tracking_evidence').fetchone()[0]

    # Contact data completeness
    has_contact = conn.execute("""
        SELECT COUNT(*) FROM alumni WHERE
        (email IS NOT NULL AND email != '') OR
        (no_hp IS NOT NULL AND no_hp != '') OR
        (linkedin IS NOT NULL AND linkedin != '')
    """).fetchone()[0]

    has_job = conn.execute("""
        SELECT COUNT(*) FROM alumni WHERE
        tempat_bekerja IS NOT NULL AND tempat_bekerja != ''
    """).fetchone()[0]

    # Stats by prodi
    prodi_stats = conn.execute('''
        SELECT prodi, COUNT(*) as jumlah,
               SUM(CASE WHEN status = 'sudah_dilacak' THEN 1 ELSE 0 END) as dilacak
        FROM alumni GROUP BY prodi ORDER BY jumlah DESC LIMIT 20
    ''').fetchall()

    # Stats by fakultas
    fakultas_stats = conn.execute('''
        SELECT fakultas, COUNT(*) as jumlah
        FROM alumni WHERE fakultas IS NOT NULL
        GROUP BY fakultas ORDER BY jumlah DESC
    ''').fetchall()

    # Recent evidence
    recent_evidence = conn.execute('''
        SELECT * FROM tracking_evidence ORDER BY tanggal_ditemukan DESC LIMIT 5
    ''').fetchall()

    conn.close()

    return {
        'total': total,
        'sudah_dilacak': sudah,
        'belum_dilacak': belum,
        'perlu_verifikasi': verifikasi,
        'evidence_count': evidence_count,
        'has_contact': has_contact,
        'has_job': has_job,
        'prodi_stats': [dict(r) for r in prodi_stats],
        'fakultas_stats': [dict(r) for r in fakultas_stats],
        'recent_evidence': [dict(r) for r in recent_evidence]
    }
