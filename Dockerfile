FROM python:3.10.0
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY req.txt /code/req.txt

RUN pip install -r /code/req.txt

COPY . /code/

CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--ws", "websockets"]