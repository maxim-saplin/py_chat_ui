# FROM python:3.11-slim
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
ENV API_TYPE Empty
ENV DISABLE_AUTH False
CMD ["streamlit", "run", "main.py"]