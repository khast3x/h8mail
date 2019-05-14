FROM python:3-alpine

RUN apk add --update --no-cache git
WORKDIR h8mail
RUN pip3 install requests
COPY . .
ENTRYPOINT ["python", "h8mail.py"]
CMD ["-h"]
