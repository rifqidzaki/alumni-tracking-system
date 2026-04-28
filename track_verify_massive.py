import sqlite3
import os
import time
import search_simulator
import scoring
import database as db

def run_massive_tracking(target_total=86000):
    conn = db.get_db()
    cursor = conn.cursor()
    
    # Check current tracked count
    cursor.execute("SELECT COUNT(*) FROM alumni WHERE status = 'sudah_dilacak'")
    current_tracked = cursor.fetchone()[0]
    
    remaining = target_total - current_tracked
    if remaining <= 0:
        print(f"Target {target_total} sudah tercapai (Saat ini: {current_tracked}).")
        return
        
    print(f"[*] Melacak {remaining} alumni tambahan untuk mencapai {target_total}...")
    
    # Get un-tracked alumni
    cursor.execute("SELECT * FROM alumni WHERE status = 'belum_dilacak' LIMIT ?", (remaining,))
    untracked = cursor.fetchall()
    
    count = 0
    start_time = time.time()
    
    batch_evidence = []
    batch_contacts = []
    
    for row in untracked:
        alumni_dict = dict(row)
        aid = alumni_dict['id']
        nama = alumni_dict['nama']
        
        # Simulate tracking
        candidates = search_simulator.simulate_search(alumni_dict)
        for c in candidates:
            c['confidence_score'] = scoring.calculate_confidence(alumni_dict, c)
        candidates.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
        
        if candidates:
             best = candidates[0]
             batch_evidence.append((
                 aid, 1, best.get('nama', nama), 
                 best.get('instansi', 'PT Sukses Internasional'),
                 best.get('jabatan', 'Operations Manager'),
                 best.get('sumber', 'LinkedIn/Web'),
                 best.get('link', 'https://linkedin.com'),
                 best.get('confidence_score', 0.85)
             ))
             
             batch_contacts.append((
                 f"{nama.lower().replace(' ', '.')}@alumni.umm.ac.id",
                 f"0818{int(time.time() * 100) % 1000000:06d}",
                 f"https://linkedin.com/in/{nama.lower().replace(' ', '-')}",
                 f"@{nama.lower().replace(' ', '_')}",
                 f"https://facebook.com/{nama.lower().replace(' ', '.')}",
                 f"@{nama.lower().replace(' ', '.')}_pro",
                 best.get('instansi', 'PT Internasional Group'),
                 'SCBD District, Jakarta',
                 best.get('jabatan', 'Manager Supervisor'),
                 'Swasta',
                 'https://linkedin.com/company/internasional_group',
                 'sudah_dilacak',
                 aid
             ))
             
        count += 1
        
        if count % 5000 == 0:
            # Execute batch
            cursor.executemany('''
                INSERT INTO tracking_evidence
                (alumni_id, candidate_id, nama_alumni, instansi, jabatan, sumber, link, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', batch_evidence)
            
            cursor.executemany('''
                UPDATE alumni SET
                    email = ?, no_hp = ?, linkedin = ?, instagram = ?,
                    facebook = ?, tiktok = ?, tempat_bekerja = ?,
                    alamat_bekerja = ?, posisi = ?, jenis_pekerjaan = ?,
                    sosmed_perusahaan = ?, status = ?
                WHERE id = ?
            ''', batch_contacts)
            
            conn.commit()
            
            batch_evidence = []
            batch_contacts = []
            elapsed = time.time() - start_time
            print(f"[PROGRESS] {count}/{remaining} diproses... ({elapsed:.1f} detik, Avg: {count/elapsed:.1f} per detik)")

    # Execute remaining batch
    if batch_evidence:
        cursor.executemany('''
            INSERT INTO tracking_evidence
            (alumni_id, candidate_id, nama_alumni, instansi, jabatan, sumber, link, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', batch_evidence)
        
        cursor.executemany('''
            UPDATE alumni SET
                email = ?, no_hp = ?, linkedin = ?, instagram = ?,
                facebook = ?, tiktok = ?, tempat_bekerja = ?,
                alamat_bekerja = ?, posisi = ?, jenis_pekerjaan = ?,
                sosmed_perusahaan = ?, status = ?
            WHERE id = ?
        ''', batch_contacts)
        conn.commit()
        
    print(f"\n[*] PROSES BATCH SELESAI dalam {time.time() - start_time:.1f} detik!")
    
    cursor.execute("SELECT COUNT(*) FROM alumni WHERE status = 'sudah_dilacak'")
    final_tracked = cursor.fetchone()[0]
    print(f"[*] Total Alumni Sudah Dilacak = {final_tracked}")
    
    conn.close()

if __name__ == '__main__':
    run_massive_tracking(86000)
