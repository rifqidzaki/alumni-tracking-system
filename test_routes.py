"""Test all routes for the Alumni Tracking System."""
import urllib.request
import urllib.parse

base = "http://127.0.0.1:5000"
results = []

def test_get(name, path):
    try:
        r = urllib.request.urlopen(f"{base}{path}")
        code = r.getcode()
        results.append((name, code, "PASS" if code == 200 else "FAIL"))
    except Exception as e:
        results.append((name, str(e), "FAIL"))

def test_post(name, path, data):
    try:
        encoded = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(f"{base}{path}", data=encoded, method="POST")
        r = urllib.request.urlopen(req)
        code = r.getcode()
        results.append((name, code, "PASS" if code == 200 else "FAIL"))
    except urllib.error.HTTPError as e:
        if e.code in (302, 308):
            results.append((name, "302 redirect", "PASS"))
        else:
            results.append((name, f"HTTP {e.code}", "FAIL"))
    except Exception as e:
        results.append((name, str(e), "FAIL"))

test_get("Dashboard", "/")
test_get("Alumni Add Form", "/alumni/add")
test_get("Alumni List", "/alumni/list")
test_get("Query Result", "/alumni/1/query")
test_get("Search Result", "/alumni/1/search")
test_get("Evidence Page", "/evidence")
test_get("API Dashboard Stats", "/api/dashboard-stats")

test_post("Add Alumni", "/alumni/add", {
    "nama": "Test User", "prodi": "Informatika",
    "tahun_lulus": "2023", "kota": "Malang", "email": "test@mail.com"
})
test_post("Save Evidence", "/alumni/1/save-evidence", {
    "candidate_id": "1", "nama_alumni": "Budi Santoso",
    "instansi": "UMM", "jabatan": "Developer",
    "sumber": "LinkedIn", "link": "https://linkedin.com/in/budi",
    "confidence_score": "0.85"
})

print("=" * 60)
print("ROUTE TEST RESULTS")
print("=" * 60)
for name, status, result in results:
    print(f"  {result} | {status} | {name}")
print("=" * 60)
total_pass = sum(1 for _, _, r in results if r == "PASS")
print(f"Total: {total_pass}/{len(results)} passed")
