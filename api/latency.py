import json
import statistics
import math
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

def percentile(data, percent):
    k = (len(data)-1) * percent / 100
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return data[int(k)]
    d0 = data[int(f)] * (c-k)
    d1 = data[int(c)] * (k-f)
    return d0+d1

@app.post("/api/latency")
async def latency(request: Request):
    body = await request.json()
    regions = body["regions"]
    threshold = body["threshold_ms"]

    with open("telemetry.json") as f:
        data = json.load(f)

    result = {}

    for region in regions:
        records = [r for r in data if r["region"] == region]

        latencies = sorted([r["latency_ms"] for r in records])
        uptimes = [r["uptime_pct"] for r in records]

        result[region] = {
            "avg_latency": statistics.mean(latencies),
            "p95_latency": percentile(latencies, 95),
            "avg_uptime": statistics.mean(uptimes),
            "breaches": len([l for l in latencies if l > threshold])
        }

    return result
