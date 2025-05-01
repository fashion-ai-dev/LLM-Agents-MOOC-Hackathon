FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3001

CMD ["watchmedo", "auto-restart", "--directory=./", "--pattern=*.py", "--recursive", "--observer-polling", "--", "python", "-u", "app.py"]

