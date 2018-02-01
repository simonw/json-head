FROM python:3
COPY ./requirements.txt /app/
RUN pip install -r /app/requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 8006
CMD ["python", "json_head.py"]
