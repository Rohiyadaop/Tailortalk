FROM python:3.11-slim
WORKDIR /app
COPY ./frontend /app
RUN pip install --upgrade pip && pip install streamlit requests
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
