FROM python:3.11-slim-bookworm

# Comment this out if want to see the output messages
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libpulse0 \
    pulseaudio-utils \
    pipewire \
    pipewire-bin \
    alsa-utils \
    libportaudio2 \
    libasound2-plugins \
    libpulse0 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY .asoundrc /root/.asoundrc
COPY . .

EXPOSE 5000

CMD ["python", "-m", "app.main"]