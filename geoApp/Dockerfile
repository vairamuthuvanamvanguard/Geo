FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt .
RUN pip install --upgrade pip \
    && apt-get update \
    && apt-get install -y libgdal-dev \
    && GDAL_VERSION=$(gdal-config --version) \
    && pip install GDAL==$GDAL_VERSION \
    && pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]

