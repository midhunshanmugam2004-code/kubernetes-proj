FROM python:3.12-alpine
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DATA_DIR=/data
WORKDIR /app
COPY app/app.py /app/app.py
RUN addgroup -S appgroup && adduser -S appuser -G appgroup && mkdir -p /data && chown -R appuser:appgroup /app /data
USER appuser
EXPOSE 8080
CMD ["python", "/app/app.py"]
