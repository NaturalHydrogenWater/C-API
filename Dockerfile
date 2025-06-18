FROM python:3.13.5-alpine3.22

RUN apk add --no-cache gcc musl-dev
WORKDIR /app
COPY app.py /app/
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5100
CMD ["python", "app.py"]