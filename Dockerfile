FROM python:3

WORKDIR /usr/src/appdata

COPY requirements.txt ./
RUN apt-get install libgeos-dev 
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./lance.py" ]
