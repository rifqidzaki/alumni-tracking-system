"""
Alumni Tracking System - Main Flask Application
A web-based system for tracking university alumni through public sources.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database as db
import scoring
import search_simulator

app = Flask(__name__)
app.secret_key = 'alumni-tracking-secret-key-2026'


# ─── Initialize DB on startup ────────────────────────────────
with app.app_context():
    db.init_db()


# ─── Dashboard ────────────────────────────────────────────────

@app.route('/')
def dashboard():
    stats = db.get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)


@app.route('/api/dashboard-stats')
def api_dashboard_stats():
    stats = db.get_dashboard_stats()
    return jsonify(stats)


# ─── Alumni CRUD ──────────────────────────────────────────────

@app.route('/alumni/add', methods=['GET', 'POST'])
def alumni_add():
    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        prodi = request.form.get('prodi', '').strip()
        tahun_lulus = request.form.get('tahun_lulus', '').strip()
        kota = request.form.get('kota', '').strip()
        email = request.form.get('email', '').strip() or None

        if not nama or not prodi or not tahun_lulus or not kota:
            flash('Semua field wajib harus diisi!', 'danger')
            return redirect(url_for('alumni_add'))

        try:
            tahun_lulus = int(tahun_lulus)
        except ValueError:
            flash('Tahun lulus harus berupa angka!', 'danger')
            return redirect(url_for('alumni_add'))

        db.add_alumni(nama, prodi, tahun_lulus, kota, email)
        flash(f'Alumni "{nama}" berhasil ditambahkan!', 'success')
        return redirect(url_for('alumni_list'))

    return render_template('alumni_form.html')


@app.route('/alumni/list')
def alumni_list():
    search = request.args.get('search', '').strip()
    prodi_filter = request.args.get('prodi', '').strip()
    tahun_filter = request.args.get('tahun', '').strip()
    page = request.args.get('page', 1, type=int)

    alumni_data, total, total_pages = db.get_all_alumni(
        search=search or None,
        prodi_filter=prodi_filter or None,
        tahun_filter=tahun_filter or None,
        page=page
    )

    prodi_list = db.get_all_prodi()
    tahun_list = db.get_all_tahun()

    return render_template('alumni_form.html',
                           alumni_list=alumni_data,
                           total=total,
                           total_pages=total_pages,
                           current_page=page,
                           search=search,
                           prodi_filter=prodi_filter,
                           tahun_filter=tahun_filter,
                           prodi_list=prodi_list,
                           tahun_list=tahun_list,
                           show_list=True)


# ─── Generate Query ──────────────────────────────────────────

@app.route('/alumni/<int:alumni_id>/query')
def query_result(alumni_id):
    alumni = db.get_alumni_by_id(alumni_id)
    if not alumni:
        flash('Alumni tidak ditemukan!', 'danger')
        return redirect(url_for('alumni_list'))

    queries = scoring.generate_queries(dict(alumni))
    return render_template('query_result.html', alumni=alumni, queries=queries)


# ─── Search Results & Disambiguation ─────────────────────────

@app.route('/alumni/<int:alumni_id>/search')
def search_result(alumni_id):
    alumni = db.get_alumni_by_id(alumni_id)
    if not alumni:
        flash('Alumni tidak ditemukan!', 'danger')
        return redirect(url_for('alumni_list'))

    alumni_dict = dict(alumni)

    # Simulate search
    candidates = search_simulator.simulate_search(alumni_dict)

    # Calculate confidence scores
    for c in candidates:
        c['confidence_score'] = scoring.calculate_confidence(alumni_dict, c)

    # Cross-validate
    candidates = scoring.cross_validate(candidates)

    # Classify
    for c in candidates:
        c['status'] = scoring.classify(c['confidence_score'])
        c['status_label'] = scoring.classify_label(c['status'])
        c['status_badge'] = scoring.classify_badge(c['status'])

    # Sort by score desc
    candidates.sort(key=lambda x: x['confidence_score'], reverse=True)

    # Save candidates to database
    db.save_candidates(alumni_id, candidates)

    return render_template('search_result.html', alumni=alumni, candidates=candidates)


# ─── Save Evidence ───────────────────────────────────────────

@app.route('/alumni/<int:alumni_id>/save-evidence', methods=['POST'])
def save_evidence(alumni_id):
    alumni = db.get_alumni_by_id(alumni_id)
    if not alumni:
        flash('Alumni tidak ditemukan!', 'danger')
        return redirect(url_for('alumni_list'))

    candidate_id = request.form.get('candidate_id', type=int)
    nama_alumni = request.form.get('nama_alumni', '')
    instansi = request.form.get('instansi', '')
    jabatan = request.form.get('jabatan', '')
    sumber = request.form.get('sumber', '')
    link = request.form.get('link', '')
    confidence_score = request.form.get('confidence_score', 0, type=float)

    db.save_evidence(alumni_id, candidate_id, nama_alumni, instansi, jabatan, sumber, link, confidence_score)
    flash(f'Bukti pelacakan untuk "{alumni["nama"]}" berhasil disimpan!', 'success')
    return redirect(url_for('search_result', alumni_id=alumni_id))


# ─── Tracking Evidence ──────────────────────────────────────

@app.route('/evidence')
def evidence():
    page = request.args.get('page', 1, type=int)
    evidence_list, total, total_pages = db.get_all_evidence(page=page)
    return render_template('evidence.html',
                           evidence_list=evidence_list,
                           total=total,
                           total_pages=total_pages,
                           current_page=page)


# ─── Run ─────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
