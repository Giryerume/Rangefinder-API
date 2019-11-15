FROM python:3

MAINTAINER guigashad@gmail.com

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3"]

CMD ["app.py"]
