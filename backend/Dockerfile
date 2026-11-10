FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt requirements-ml.txt ./
ARG ENABLE_ML=false
RUN pip install --no-cache-dir -r requirements.txt && if [ "$ENABLE_ML" = "true" ]; then pip install --no-cache-dir -r requirements-ml.txt; fi
COPY app ./app
COPY models ./models
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
