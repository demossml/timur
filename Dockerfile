FROM duffn/python-poetry:3.10-slim-1.1.12-2022-01-21


WORKDIR /app

# Установка unrar
RUN apt-get update && apt-get install -y unrar-free

COPY . .

RUN poetry install

CMD ["sh"]

