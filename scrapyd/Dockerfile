FROM python:3.10
WORKDIR /app
RUN mkdir ./logs
COPY scrapyd.conf /etc/scrapyd/
COPY requirements.txt .
EXPOSE 6800

ENV TZ=Asia/Shanghai

RUN apt-get update && apt-get install -y chromium

ENV DRISSIONPAGE_CHROME_PATH=/usr/bin/chromium
ENV DRISSIONPAGE_DOWNLOAD_PATH=/app/downloads

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
CMD mkdir /root/logs
CMD logparser -dir ./logs & scrapyd
