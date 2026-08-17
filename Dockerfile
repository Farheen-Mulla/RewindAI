FROM python:3.11-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

ENV HF_HOME=/tmp/hf_cache
ENV TRANSFORMERS_CACHE=/tmp/hf_cache
ENV SENTENCE_TRANSFORMERS_HOME=/tmp/hf_cache
ENV CHROMA_DIR=/tmp/chroma_db

COPY --chown=user solution/backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user solution/backend/app ./app
COPY --chown=user solution/frontend ../frontend
COPY --chown=user solution/data ../data

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]