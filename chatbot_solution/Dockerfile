# TBD
FROM python:3.11-slim

RUN pip install poetry

WORKDIR /app

COPY ./ /app/.

RUN poetry install --no-root

EXPOSE 8501

CMD poetry run streamlit run app.py --server.port 8503
