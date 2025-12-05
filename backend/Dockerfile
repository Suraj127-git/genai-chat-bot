FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY backend/pyproject.toml /app/backend/pyproject.toml
COPY backend/AINews /app/AINews
COPY backend/app /app/backend/app
RUN pip install uv && python - << 'PY'
import tomllib, pathlib
data = tomllib.loads(pathlib.Path('/app/backend/pyproject.toml').read_text())
deps = data['project']['dependencies']
pathlib.Path('/app/requirements.txt').write_text('\n'.join(deps))
PY
RUN uv pip install -r /app/requirements.txt
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn","backend.app.main:app","--host","0.0.0.0","--port","8000"]
