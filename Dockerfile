FROM python:3

WORKDIR /smocka

ADD app.py /
ADD manage.py /

COPY app /app
COPY public /public

ADD requirements.txt /

RUN pip install -r /requirements.txt

RUN python /manage.py --init-app

CMD [ "python", "./app.py" ]