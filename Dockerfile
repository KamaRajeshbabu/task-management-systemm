FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
RUN chmod +x ./scripts/entrypoint.sh || true
EXPOSE 8000
ENTRYPOINT ["./scripts/entrypoint.sh"]
