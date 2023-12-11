FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
ENV DISABLE_AUTH True
CMD ["streamlit", "run", "main.py"]