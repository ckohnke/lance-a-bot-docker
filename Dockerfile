FROM python:3

WORKDIR /usr/src/appdata

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./lance.py" ]