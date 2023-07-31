FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install --no-install-recommends --assume-yes curl libpq-dev gcc python3-dev

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

WORKDIR /app
COPY . .

CMD python3 main.py 2>&1 | tee -a connector.log
