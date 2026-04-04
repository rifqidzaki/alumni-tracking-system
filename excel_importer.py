"""
Excel importer for Alumni Tracking System.
Reads Alumni 2000-2025.xlsx and imports into SQLite.
"""

import openpyxl
import os
import database as db


EXCEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Alumni 2000-2025.xlsx')


def import_excel(filepath=None, batch_size=5000):
    """Import alumni data from Excel file in batches.
    Returns (imported_count, skipped_count, error_count).
    """
    if filepath is None:
        filepath = EXCEL_PATH

    if not os.path.exists(filepath):
        print(f"[importer] File not found: {filepath}")
        return 0, 0, 0

    print(f"[importer] Opening {filepath}...")
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    ws = wb.active

    imported = 0
    skipped = 0
    errors = 0
    batch = []

    print(f"[importer] Reading rows...")
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        try:
            if len(row) < 6:
                skipped += 1
                continue

            nama = str(row[0]).strip() if row[0] else None
            nim = str(row[1]).strip() if row[1] else None
            tahun_masuk = str(row[2]).strip() if row[2] else None
            tanggal_lulus = str(row[3]).strip() if row[3] else None
            fakultas = str(row[4]).strip() if row[4] else None
            prodi = str(row[5]).strip() if row[5] else None

            if not nama or nama == 'None':
                skipped += 1
                continue

            if not prodi or prodi == 'None':
                prodi = 'Tidak Diketahui'

            # Extract tahun_lulus from tanggal_lulus or tahun_masuk
            tahun_lulus = 0
            if tanggal_lulus and tanggal_lulus != 'None':
                try:
                    # Try to extract year from date string
                    parts = str(tanggal_lulus).split('-')
                    if len(parts) >= 1:
                        yr = int(parts[0][:4])
                        if 1990 <= yr <= 2030:
                            tahun_lulus = yr
                except (ValueError, IndexError):
                    pass

            if tahun_lulus == 0 and tahun_masuk and tahun_masuk != 'None':
                try:
                    yr = int(str(tahun_masuk)[:4])
                    tahun_lulus = yr + 4  # estimate
                except (ValueError, IndexError):
                    tahun_lulus = 2020

            if tahun_lulus == 0:
                tahun_lulus = 2020

            kota = "Malang"  # UMM default

            # (nama, nim, tahun_masuk, tanggal_lulus, fakultas, prodi, tahun_lulus, kota)
            batch.append((nama, nim, tahun_masuk, tanggal_lulus, fakultas, prodi, tahun_lulus, kota))

            if len(batch) >= batch_size:
                count = db.add_alumni_bulk(batch)
                imported += count
                if (imported % 10000) == 0:
                    print(f"[importer] ... {imported} rows imported")
                batch = []

        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"[importer] Error row {row_idx}: {e}")

    # Final batch
    if batch:
        count = db.add_alumni_bulk(batch)
        imported += count

    wb.close()
    print(f"[importer] Done! Imported: {imported}, Skipped: {skipped}, Errors: {errors}")
    return imported, skipped, errors


if __name__ == '__main__':
    db.init_db()
    import_excel()
