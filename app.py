"""
Alumni Tracking System - Main Flask Application
Extended with: authentication, Excel import, alumni detail/contact editing.
"""

from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import database as db
import scoring
import search_simulator
import pddikti_verifier

app = Flask(__name__)
app.secret_key = 'alumni-tracking-secret-key-2026'


# ─── Initialize DB on startup ────────────────────────────────
with app.app_context():
    db.init_db()


# ─── Auth Decorator ──────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ─── Auth Routes ──────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = db.verify_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['nama_lengkap'] = user['nama_lengkap'] or user['username']
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah!', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah keluar.', 'info')
    return redirect(url_for('login'))


# ─── Dashboard ────────────────────────────────────────────────

@app.route('/')
@login_required
def dashboard():
    stats = db.get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)


@app.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    stats = db.get_dashboard_stats()
    return jsonify(stats)


# ─── Alumni CRUD ──────────────────────────────────────────────

@app.route('/alumni/add', methods=['GET', 'POST'])
@login_required
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
@login_required
def alumni_list():
    search = request.args.get('search', '').strip()
    prodi_filter = request.args.get('prodi', '').strip()
    tahun_filter = request.args.get('tahun', '').strip()
    fakultas_filter = request.args.get('fakultas', '').strip()
    page = request.args.get('page', 1, type=int)

    alumni_data, total, total_pages = db.get_all_alumni(
        search=search or None,
        prodi_filter=prodi_filter or None,
        tahun_filter=tahun_filter or None,
        fakultas_filter=fakultas_filter or None,
        page=page,
        per_page=25
    )

    prodi_list = db.get_all_prodi()
    tahun_list = db.get_all_tahun()
    fakultas_list = db.get_all_fakultas()

    return render_template('alumni_form.html',
                           alumni_list=alumni_data,
                           total=total,
                           total_pages=total_pages,
                           current_page=page,
                           search=search,
                           prodi_filter=prodi_filter,
                           tahun_filter=tahun_filter,
                           fakultas_filter=fakultas_filter,
                           prodi_list=prodi_list,
                           tahun_list=tahun_list,
                           fakultas_list=fakultas_list,
                           show_list=True)


# ─── Alumni Detail & Contact Edit ────────────────────────────

@app.route('/alumni/<int:alumni_id>/detail')
@login_required
def alumni_detail(alumni_id):
    alumni = db.get_alumni_by_id(alumni_id)
    if not alumni:
        flash('Alumni tidak ditemukan!', 'danger')
        return redirect(url_for('alumni_list'))
    return render_template('alumni_detail.html', alumni=alumni)


@app.route('/alumni/<int:alumni_id>/update-contact', methods=['POST'])
@login_required
def alumni_update_contact(alumni_id):
    alumni = db.get_alumni_by_id(alumni_id)
    if not alumni:
        flash('Alumni tidak ditemukan!', 'danger')
        return redirect(url_for('alumni_list'))

    data = {
        'email': request.form.get('email', '').strip() or None,
        'no_hp': request.form.get('no_hp', '').strip() or None,
        'linkedin': request.form.get('linkedin', '').strip() or None,
        'instagram': request.form.get('instagram', '').strip() or None,
        'facebook': request.form.get('facebook', '').strip() or None,
        'tiktok': request.form.get('tiktok', '').strip() or None,
        'tempat_bekerja': request.form.get('tempat_bekerja', '').strip() or None,
        'alamat_bekerja': request.form.get('alamat_bekerja', '').strip() or None,
        'posisi': request.form.get('posisi', '').strip() or None,
        'jenis_pekerjaan': request.form.get('jenis_pekerjaan', '').strip() or None,
        'sosmed_perusahaan': request.form.get('sosmed_perusahaan', '').strip() or None,
    }

    db.update_alumni_contact(alumni_id, data)
    flash(f'Data kontak "{alumni["nama"]}" berhasil diperbarui!', 'success')
    return redirect(url_for('alumni_detail', alumni_id=alumni_id))


# ─── Excel Import ────────────────────────────────────────────

@app.route('/import-excel')
@login_required
def import_excel_page():
    stats = db.get_dashboard_stats()
    return render_template('import_excel.html', stats=stats)


@app.route('/import-excel/run', methods=['POST'])
@login_required
def import_excel_run():
    import excel_importer
    import os
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Alumni 2000-2025.xlsx')
    if not os.path.exists(filepath):
        flash('File Excel tidak ditemukan!', 'danger')
        return redirect(url_for('import_excel_page'))

    imported, skipped, errors = excel_importer.import_excel(filepath)
    flash(f'Import selesai! {imported} data diimpor, {skipped} dilewati, {errors} error.', 'success')
    return redirect(url_for('alumni_list'))


# ─── Generate Query ──────────────────────────────────────────

@app.route('/alumni/<int:alumni_id>/query')
@login_required
def query_result(alumni_id):
    alumni = db.get_alumni_by_id(alumni_id)
    if not alumni:
        flash('Alumni tidak ditemukan!', 'danger')
        return redirect(url_for('alumni_list'))

    queries = scoring.generate_queries(dict(alumni))
    return render_template('query_result.html', alumni=alumni, queries=queries)


# ─── Search Results & Disambiguation ─────────────────────────

@app.route('/alumni/<int:alumni_id>/search')
@login_required
def search_result(alumni_id):
    alumni = db.get_alumni_by_id(alumni_id)
    if not alumni:
        flash('Alumni tidak ditemukan!', 'danger')
        return redirect(url_for('alumni_list'))

    alumni_dict = dict(alumni)
    candidates = search_simulator.simulate_search(alumni_dict)

    for c in candidates:
        c['confidence_score'] = scoring.calculate_confidence(alumni_dict, c)
    candidates = scoring.cross_validate(candidates)
    for c in candidates:
        c['status'] = scoring.classify(c['confidence_score'])
        c['status_label'] = scoring.classify_label(c['status'])
        c['status_badge'] = scoring.classify_badge(c['status'])
    candidates.sort(key=lambda x: x['confidence_score'], reverse=True)
    db.save_candidates(alumni_id, candidates)

    return render_template('search_result.html', alumni=alumni, candidates=candidates)


# ─── Save Evidence ───────────────────────────────────────────

@app.route('/alumni/<int:alumni_id>/save-evidence', methods=['POST'])
@login_required
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


# ─── PDDIKTI Verification ───────────────────────────────────

@app.route('/alumni/<int:alumni_id>/pddikti')
@login_required
def pddikti_verify(alumni_id):
    alumni = db.get_alumni_by_id(alumni_id)
    if not alumni:
        flash('Alumni tidak ditemukan!', 'danger')
        return redirect(url_for('alumni_list'))

    result = pddikti_verifier.verify_alumni(dict(alumni))
    return render_template('pddikti.html', alumni=alumni, result=result)


# ─── Tracking Evidence ──────────────────────────────────────

@app.route('/evidence')
@login_required
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
