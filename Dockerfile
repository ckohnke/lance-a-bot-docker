FROM python:3

COPY requirements.txt ./
RUN apt-get update && apt-get -y install libgeos-dev 
RUN pip install --no-cache-dir -r requirements.txt

COPY lance.py /app/lance.py

CMD [ "python", "/app/lance.py" ]
