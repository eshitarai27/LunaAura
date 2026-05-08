import requests
import time
import concurrent.futures
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

URL = "http://127.0.0.1:5001/predict"
PAYLOAD = {
  "username": "LoadTestUser",
  "Age": 28,
  "Gender": "Female",
  "Sleep Duration": 7.0,
  "Stress Level": 5,
  "Cycle_Day": 14,
  "Physical Activity Level": 30,
  "anxiety_level": 4,
  "water_intake": 2.0
}

TOTAL_REQUESTS = 150
CONCURRENCY = 10

def send_request(req_id):
    start = time.time()
    try:
        r = requests.post(URL, json=PAYLOAD, timeout=5)
        status = r.status_code
    except Exception as e:
        status = 500
    end = time.time()
    return req_id, (end - start) * 1000, status  # return time in ms

print(f"Starting Load Test: {TOTAL_REQUESTS} requests, Concurrency {CONCURRENCY}")

results = []
start_test_time = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
    futures = [executor.submit(send_request, i) for i in range(TOTAL_REQUESTS)]
    for future in concurrent.futures.as_completed(futures):
        results.append(future.result())

total_duration = time.time() - start_test_time
print(f"Test completed in {total_duration:.2f} seconds.")

# Prepare data for plotting
response_times = [r[1] for r in results]
successful_requests = sum(1 for r in results if r[2] == 200)

mean_rt = np.mean(response_times)
p95_rt = np.percentile(response_times, 95)

# Plotting
fig, ax = plt.subplots(figsize=(10, 5))

# Scatter and line
ax.plot(range(len(response_times)), response_times, color='#3b82f6', alpha=0.8, linewidth=1.2, marker='o', markersize=4, label='Response Time')

# Reference lines
ax.axhline(mean_rt, color='#ef4444', linestyle='-', linewidth=2, label=f'Mean ({mean_rt:.1f} ms)')
ax.axhline(p95_rt, color='#f59e0b', linestyle='--', linewidth=2, label=f'95th Pctl ({p95_rt:.1f} ms)')

# Styling
ax.set_title(f'LunaAura API Load Test (/predict Endpoint)\n{TOTAL_REQUESTS} requests at concurrency {CONCURRENCY} | Success Rate: {(successful_requests/TOTAL_REQUESTS)*100:.1f}%', fontweight='bold', pad=15)
ax.set_xlabel('Request Completion Sequence', fontweight='bold')
ax.set_ylabel('Response Time (ms)', fontweight='bold')
ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.legend()

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
out_path = '/Users/prashantkumar/Desktop/Luna_Aura/paper_assets/backend_response_time.png'
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Graph saved to {out_path}")
