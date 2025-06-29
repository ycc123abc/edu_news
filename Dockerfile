FROM python:3.10

# 设置时区
ENV TZ=Asia/Shanghai

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    fonts-noto-cjk


WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV DRISSIONPAGE_CHROME_PATH=/usr/bin/chromium
ENV DRISSIONPAGE_DOWNLOAD_PATH=/app/downloads

COPY . .

CMD ["python", "run.py"]