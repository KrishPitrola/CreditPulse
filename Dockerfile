# Dockerfile
# Containerizes the FastAPI service. Build and run with:
#   docker build -t credit-pipeline-api .
#   docker run -p 8000:8000 credit-pipeline-api
# Then open http://127.0.0.1:8000/docs

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make sure the database exists inside the image (built at image-build time)
RUN python load_data.py

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
