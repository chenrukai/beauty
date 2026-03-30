FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 ffmpeg \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pip==25.0.1 setuptools==75.9.1 wheel==0.45.1 \
    && pip install --no-cache-dir --no-build-isolation -r requirements.txt

COPY main.py ./

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
