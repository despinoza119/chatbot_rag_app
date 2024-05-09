# TBD
FROM python:3.11-slim

WORKDIR /usr/src/app

COPY ./ /usr/src/app

RUN pip install -r requirements.txt

EXPOSE 8501

ENV OPENAI_API_KEY=sk-proj-kBrAPo96dNsavQKwbwVmT3BlbkFJ3rSZkgqPxzsTp3T2Hny5

CMD ["streamlit", "run", "application.py"]

