FROM python:3.12-slim

WORKDIR /app

RUN apt-get update -y \n    && apt-get install -y --no-install-recommends build-essential \n    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \n    && pip install --no-cache-dir uv \n    && uv pip install -r <(python - <<'PY'
import tomllib, sys
print('
'.join(tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']))
PY
)

COPY app app
COPY .env .env

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
