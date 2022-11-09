FROM python:3.10.8-alpine3.16

LABEL maintainer="Aman Maharjan<mhrznamn068@gmail.com>"

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r ./requirements.txt

COPY ./app .

CMD ["flask", "run", "--host=0.0.0.0"]
