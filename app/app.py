# app/app.py
from flask import Flask, Response
from prometheus_client import Counter, Histogram, generate_latest
import time
import random

app = Flask(__name__)

# Métricas do Prometheus
REQUEST_LATENCY = Histogram('http_request_latency_seconds', 'Request latency', ['endpoint'])
REQUEST_COUNT = Counter('http_requests_total', 'Total requests', ['endpoint', 'status'])
ERROR_COUNT = Counter('http_errors_total', 'Total errors', ['endpoint'])

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')

@app.route('/ok')
def ok():
    start_time = time.time()
    REQUEST_COUNT.labels(endpoint='/ok', status='200').inc()
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint='/ok').observe(latency)
    return "OK", 200

@app.route('/slow')
def slow():
    start_time = time.time()
    # Simula latência alta
    sleep_time = random.uniform(1, 3)
    time.sleep(sleep_time)
    REQUEST_COUNT.labels(endpoint='/slow', status='200').inc()
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint='/slow').observe(latency)
    return f"Slow response after {sleep_time:.2f} seconds", 200

@app.route('/error')
def error():
    start_time = time.time()
    ERROR_COUNT.labels(endpoint='/error').inc()
    REQUEST_COUNT.labels(endpoint='/error', status='500').inc()
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint='/error').observe(latency)
    return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)