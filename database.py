"""
Database module for Alumni Tracking System.
Handles SQLite database initialization and CRUD operations.
"""

import sqlite3
import os
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
        CREATE TABLE IF NOT EXISTS alumni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            prodi TEXT NOT NULL,
            tahun_lulus INTEGER NOT NULL,
            kota TEXT NOT NULL,
            email TEXT,
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

    conn.commit()
    conn.close()


# ─── Alumni CRUD ──────────────────────────────────────────────

def add_alumni(nama, prodi, tahun_lulus, kota, email=None):
    """Insert a new alumni record."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO alumni (nama, prodi, tahun_lulus, kota, email) VALUES (?, ?, ?, ?, ?)',
        (nama, prodi, tahun_lulus, kota, email)
    )
    conn.commit()
    alumni_id = cursor.lastrowid
    conn.close()
    return alumni_id


def get_all_alumni(search=None, prodi_filter=None, tahun_filter=None, page=1, per_page=10):
    """Get all alumni with optional filtering and pagination."""
    conn = get_db()
    query = 'SELECT * FROM alumni WHERE 1=1'
    params = []

    if search:
        query += ' AND (nama LIKE ? OR kota LIKE ? OR email LIKE ?)'
        like = f'%{search}%'
        params.extend([like, like, like])

    if prodi_filter:
        query += ' AND prodi = ?'
        params.append(prodi_filter)

    if tahun_filter:
        query += ' AND tahun_lulus = ?'
        params.append(int(tahun_filter))

    # Count total
    count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
    total = conn.execute(count_query, params).fetchone()[0]

    # Paginate
    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
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


# ─── Search Candidates CRUD ──────────────────────────────────

def save_candidates(alumni_id, candidates):
    """Save a list of search candidate dicts for an alumni."""
    conn = get_db()
    cursor = conn.cursor()
    # Clear old candidates for this alumni
    cursor.execute('DELETE FROM search_candidates WHERE alumni_id = ?', (alumni_id,))
    for c in candidates:
        cursor.execute('''
            INSERT INTO search_candidates
            (alumni_id, nama, instansi, jabatan, lokasi, bidang, tahun_aktivitas, sumber, link, confidence_score, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alumni_id,
            c.get('nama', ''),
            c.get('instansi', ''),
            c.get('jabatan', ''),
            c.get('lokasi', ''),
            c.get('bidang', ''),
            c.get('tahun_aktivitas', ''),
            c.get('sumber', ''),
            c.get('link', ''),
            c.get('confidence_score', 0.0),
            c.get('status', 'not_match')
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

    # Update alumni status based on score
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

    # Stats by prodi
    prodi_stats = conn.execute('''
        SELECT prodi, COUNT(*) as jumlah,
               SUM(CASE WHEN status = 'sudah_dilacak' THEN 1 ELSE 0 END) as dilacak
        FROM alumni GROUP BY prodi ORDER BY jumlah DESC
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
        'prodi_stats': [dict(r) for r in prodi_stats],
        'recent_evidence': [dict(r) for r in recent_evidence]
    }
