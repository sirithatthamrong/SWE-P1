FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app
ENV FLASK_ENV=production

EXPOSE 10000

CMD ["flask", "run", "--host=0.0.0.0", "--port=10000"]
