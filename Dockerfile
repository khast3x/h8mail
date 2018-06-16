FROM python:3-alpine

RUN apk add --update --no-cache git nodejs
RUN mkdir h8mail
WORKDIR h8mail
COPY requirements.txt ./
RUN pip install requests ; pip install -r requirements.txt
COPY h8mail.py classes.py targets.txt config.ini ./
ENTRYPOINT ["python", "h8mail.py", "-t", "targets.txt"]
