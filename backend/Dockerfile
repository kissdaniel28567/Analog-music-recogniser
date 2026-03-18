FROM python:3.11-slim-bookworm

# Comment this out if want to see the output messages
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libportaudio2 \
    ffmpeg \
    alsa-utils \
    libpulse0 \
    libasound2-plugins \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY .asoundrc /root/.asoundrc
COPY . .

EXPOSE 5000

CMD ["python", "-m", "app.main"]