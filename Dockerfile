FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# RUN apk --update add
# RUN apk add gcc libc-dev libffi-dev jpeg-dev zlib-dev libjpeg
# RUN apk add postgresql-dev
RUN pip install --upgrade pip
# RUN apk update \
    # && apk add postgresql-dev gcc python3-dev musl-dev

COPY ./requirements.txt .

# RUN pip install -r requirements.txt
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir -r requirements.txt


COPY . .

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]




