# backend
FROM python:3.12-slim

# some kind of clutter managment???
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# change to needed
WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .


EXPOSE 5000
CMD ["gunicorn", "app:app", "0.0.0.0:5000"]