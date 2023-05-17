FROM python:3

WORKDIR /usr/src/app

ENV ADMIN_USER_EMAIL=admin@admin.com
ENV ADMIN_USER_USERNAME=Admin
ENV ADMIN_USER_PASSWORD=password

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python create_db.py

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]