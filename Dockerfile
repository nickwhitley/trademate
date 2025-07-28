# Use the official lightweight Python image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "src/main.py"]

# gcloud builds submit --tag gcr.io/trademate-467219/trademate-app
# gcloud run deploy trademate-app   \
# --image gcr.io/trademate-467219/trademate-app   \
# --platform managed   \
# --region us-central1   \
# --allow-unauthenticated \
# --set-env-vars "GCS_BUCKET=trademate-bucket-1"


# 719319333800-compute@developer.gserviceaccount.com

# gcloud projects add-iam-policy-binding trademate-467219 \
#   --member=serviceAccount:719319333800-compute@developer.gserviceaccount.com \
#   --role=roles/storage.objectAdmin