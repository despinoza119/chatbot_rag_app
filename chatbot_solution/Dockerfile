# TBD
FROM python:3.11-slim

RUN pip install poetry

WORKDIR /app

COPY ./ /app/.

RUN poetry install --no-root

EXPOSE 8501

#ENV OPENAI_API_KEY=sk-proj-kBrAPo96dNsavQKwbwVmT3BlbkFJ3rSZkgqPxzsTp3T2Hny5

CMD poetry run streamlit run app.py --server.port 8503
