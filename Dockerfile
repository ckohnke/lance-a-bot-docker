FROM python:3

WORKDIR /usr/src/lance-a-bot

COPY requirements.txt ./
RUN apt-get update && apt-get -y install libgeos-dev 
RUN pip install --no-cache-dir -r requirements.txt

COPY lance.py .

VOLUME /config

CMD [ "python", "lance.py" ]
