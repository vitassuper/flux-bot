FROM python:3.11-slim-bullseye

ARG POETRY_VERSION=""

ENV POETRY_VERSION=${POETRY_VERSION}
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_IN_PROJECT=false
ENV POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install --no-install-recommends --assume-yes curl libpq-dev gcc python3-dev
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY . .

RUN poetry install --no-interaction --no-ansi

CMD ["poetry", "run", "bot"]
