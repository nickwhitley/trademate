# Use the official lightweight Python image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Run the app with Python (not uvicorn!)
CMD ["python", "src/gui/home.py"]

# gcloud builds submit --tag gcr.io/trademate-467219/trademate-app
# gcloud run deploy trademate-app \
#   --image gcr.io/trademate-467219/trademate-app \
#   --platform managed \
#   --region us-central1 \
#   --allow-unauthenticated