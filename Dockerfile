FROM python:3.11-slim

WORKDIR /app

# ---------- Azure Artifacts Auth ----------
ARG AZURE_ARTIFACTS_PAT
ARG PIP_INDEX_URL

ENV PIP_INDEX_URL=https://__token__:${AZURE_ARTIFACTS_PAT}@pkgs.dev.azure.com/devops-moogle/_packaging/coop-python-feed/pypi/simple/
ENV PIP_NO_CACHE_DIR=1
# -----------------------------------------

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY app/ app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
