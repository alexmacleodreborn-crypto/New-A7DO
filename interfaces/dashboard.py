from __future__ import annotations

from collections import deque
import threading

from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI(title="A7DO Dashboard")

loop_instance = None
state_history = deque(maxlen=120)


HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>A7DO Dashboard</title>
    <style>
        body {
            background: #0f172a;
            color: #e2e8f0;
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
        }
        .card {
            background: #1e293b;
            padding: 20px;
            border-radius: 10px;
        }
        h1, h2 {
            color: #38bdf8;
        }
        button {
            padding: 10px 14px;
            background: #38bdf8;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            color: #082f49;
            font-weight: bold;
        }
        ul {
            padding-left: 18px;
        }
        pre {
            white-space: pre-wrap;
            word-break: break-word;
        }
        .muted {
            color: #94a3b8;
        }
    </style>
</head>
<body>
<h1>A7DO Live Dashboard</h1>
<p class="muted">Live operator view for the running life loop.</p>

<div class="grid">
    <div class="card">
        <h2>State</h2>
        <p><b>Internal Time:</b> <span id="time">-</span></p>
        <p><b>Energy:</b> <span id="energy">-</span></p>
        <p><b>Strain:</b> <span id="strain">-</span></p>
        <p><b>Stage:</b> <span id="stage">-</span></p>
        <p><b>Alive:</b> <span id="alive">-</span></p>
    </div>

    <div class="card">
        <h2>Control</h2>
        <button onclick="injectEvent()">Inject Stimulus</button>
        <p class="muted">Adds a synthetic external event into memory.</p>
    </div>

    <div class="card">
        <h2>Recent Memory</h2>
        <pre id="memory">[]</pre>
    </div>

    <div class="card">
        <h2>Council</h2>
        <pre id="council">{}</pre>
    </div>

    <div class="card">
        <h2>Energy History</h2>
        <pre id="history">[]</pre>
    </div>
</div>

<script>
async function fetchState() {
    const res = await fetch('/state');
    const data = await res.json();

    if (data.error) {
        document.getElementById('time').innerText = data.error;
        return;
    }

    document.getElementById('time').innerText = data.time;
    document.getElementById('energy').innerText = data.energy;
    document.getElementById('strain').innerText = data.strain;
    document.getElementById('stage').innerText = data.stage;
    document.getElementById('alive').innerText = data.alive;
    document.getElementById('memory').innerText = JSON.stringify(data.memory, null, 2);
    document.getElementById('council').innerText = JSON.stringify(data.council, null, 2);
    document.getElementById('history').innerText = JSON.stringify(data.history.slice(-20), null, 2);
}

async function injectEvent() {
    await fetch('/inject', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            type: "external_stimulus",
            value: Math.random(),
            source: "dashboard"
        })
    });
    await fetchState();
}

setInterval(fetchState, 1000);
fetchState();
</script>

</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTML_PAGE


@app.get("/state")
def get_state():
    if not loop_instance:
        return {"error": "not running"}

    council = {}
    try:
        council = loop_instance.council.deliberate()
    except Exception:
        council = {}

    return {
        "time": loop_instance.internal_time,
        "energy": loop_instance.energy.level(),
        "strain": loop_instance.overload.strain,
        "stage": str(loop_instance.lifecycle.stage),
        "alive": loop_instance.pulse.is_alive(),
        "memory": loop_instance.memory.recent(10),
        "council": council,
        "history": list(state_history),
    }


@app.post("/inject")
def inject(event: dict):
    if loop_instance:
        loop_instance.record_memory(event, salience=0.5)
    return {"status": "ok"}


def record_state_snapshot(loop) -> None:
    state_history.append(
        {
            "time": loop.internal_time,
            "energy": loop.energy.level(),
            "strain": loop.overload.strain,
            "stage": str(loop.lifecycle.stage),
        }
    )


def start_dashboard(loop):
    global loop_instance
    loop_instance = loop

    import uvicorn

    threading.Thread(
        target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning"),
        daemon=True,
    ).start()
