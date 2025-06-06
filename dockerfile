FROM python:3.12.1

# Set working directory
WORKDIR /app


COPY requirements.txt .
RUN pip install -r requirements.txt

# Copying the rest of the code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]