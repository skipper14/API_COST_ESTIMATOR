INTERACTIVE = {
    'endpoint': 'POST /triage',
    'slo_p95_ms': 2000,
    'model': 'gpt-4o-mini',
}
BATCH = {
    'endpoint': 'POST /ingest/batch',  # Week 6 Concept 11 pattern
    'slo_p95_ms': None,                # finish before 06:00, not 2s
    'model': 'gpt-4o-mini',            # or smaller / self-host off-peak
}