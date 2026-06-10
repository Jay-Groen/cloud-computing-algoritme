import requests
import concurrent.futures

url = "https://trainingsapp-91634618477.europe-west4.run.app/api/trainingsplan"

payload = {
    "naam": "Test",
    "leeftijd": 25,
    "geslacht": "man",
    "lengte": 180,
    "gewicht": 80,
    "trainingsdoel": "spieropbouw",
    "trainingsniveau": "beginner",
    "trainingsfrequentie": 3,
    "trainingsduur": 60,
    "activiteitsniveau": "gemiddeld",
    "blessures": [],
    "beschikbare_dagen": ["maandag", "woensdag", "vrijdag"]
}

def send_request(_):
    response = requests.post(url, json=payload)
    return response.status_code

with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    results = list(executor.map(send_request, range(50)))

status_counts = {}
for status in results:
    status_counts[status] = status_counts.get(status, 0) + 1

print(f"{len(results)} requests verzonden")
for status, count in status_counts.items():
    print(f"  HTTP {status}: {count}x")
