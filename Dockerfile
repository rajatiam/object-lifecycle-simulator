FROM python:3.13-slim
WORKDIR /app
COPY object_lifecycle_simulator ./object_lifecycle_simulator
RUN useradd --uid 10001 --create-home runner
USER runner
WORKDIR /workspace
ENV PYTHONPATH=/app PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-m", "object_lifecycle_simulator"]
CMD ["--help"]
