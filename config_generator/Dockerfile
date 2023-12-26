FROM python:3.12-alpine
WORKDIR /usr/src/app
COPY . .
RUN apk add --no-cache docker-cli-compose && \
    pip install --no-cache-dir -r requirements.txt
ENV SUBNET ""
ENV IP_COUNT 100
ENV INTERVAL 3600
CMD ["python", "-u", "./app.py"]
