FROM python:alpine

COPY requirements.txt /tmp
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir -p /code
COPY *.py /code/
WORKDIR /code
ENV FLASK_APP=entrypoints/flask_app.py FLASK_DEBUG=1 PYTHONUNBUFFERED=1
CMD flask run --host=0.0.0.0 --port=80