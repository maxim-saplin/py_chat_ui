#FROM python:3.11-slim
FROM python:3.12-slim
WORKDIR /app
COPY . /app
# # 3.12, manually install Rust compiler
# RUN apt-get -y install curl build-essential gcc make && curl https://sh.rustup.rs -sSf | sh -s -- -y
# ENV PATH="/root/.cargo/bin:${PATH}"
# #
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
ENV API_TYPE Empty
ENV DISABLE_AUTH False
CMD ["streamlit", "run", "main.py"]