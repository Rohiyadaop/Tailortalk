version: '3.8'
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    image: drive-search-backend:latest
    environment:
      SERVICE_ACCOUNT_FILE: /run/secrets/service_account.json
      DRIVE_FOLDER_ID: ${DRIVE_FOLDER_ID}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app:ro
    secrets:
      - service_account

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    image: drive-search-frontend:latest
    environment:
      BACKEND_URL: ${BACKEND_URL}
    ports:
      - "8501:8501"
    depends_on:
      - backend

secrets:
  service_account:
    file: ./service-account.json
