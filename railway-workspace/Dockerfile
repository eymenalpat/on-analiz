FROM python:3.12-slim
WORKDIR /app
COPY railway-workspace/index.html /app/index.html
COPY railway-workspace/reports /app/reports
EXPOSE 8080
CMD ["python3", "-m", "http.server", "8080"]
