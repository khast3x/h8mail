FROM python:3-alpine

RUN apk add --update --no-cache git bash
WORKDIR h8mail
RUN pip3 install requests
COPY . .
RUN ["python", "setup.py", "install"]
ENTRYPOINT ["h8mail"]
CMD ["-h"]
