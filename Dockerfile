# Dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements_dash_venv.txt ./
RUN pip install --no-cache-dir -r requirements_dash_venv.txt

COPY . .

EXPOSE 80

CMD ["python", "./display_dash_app.py"]