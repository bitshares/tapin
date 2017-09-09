FROM python:3

WORKDIR /opt/faucet

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uwsgi

COPY . .
RUN python manage.py install

EXPOSE 9090

CMD [ "uwsgi", "--ini", "wsgi.ini" ]
