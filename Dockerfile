FROM python:3.10.8-alpine3.16

LABEL maintainer="Aman Maharjan<mhrznamn068@gmail.com>"

ENV USER=app

WORKDIR /app

COPY ./djangoapp/requirements.txt .

RUN adduser -D ${USER} \
    && pip install -r ./requirements.txt

COPY ./djangoapp .

RUN chown -R $USER: .

USER $USER

CMD ["python", "manage.py", "runserver", "0.0.0.0:4000"]
