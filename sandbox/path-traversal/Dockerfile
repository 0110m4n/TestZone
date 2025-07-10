FROM python:3.11-slim
WORKDIR /sandbox
COPY app/ .
RUN pip install --no-cache-dir flask
RUN useradd -ms /bin/bash sandboxuser
RUN mkdir -p /sandbox/uploads && chown sandboxuser:sandboxuser /sandbox/uploads
RUN mkdir -p /sandbox/files && chmod -R 777 /sandbox/files
USER sandboxuser
EXPOSE 8000
CMD ["python", "app.py"]

