FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

# Keep dependency installation before source-code copies so source edits reuse this layer.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY auth.py secure_triage_api.py rate_limit.py mcp_server.py agent_service.py clinics.json ./

# Do not run the API as root inside the container.
RUN addgroup --system app && adduser --system --ingroup app app \
	&& chown -R app:app /app
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
	CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "secure_triage_api:app", "--host", "0.0.0.0", "--port", "8000"]