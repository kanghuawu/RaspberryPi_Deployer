FROM resin/rpi-raspbian:latest
COPY . /app
WORKDIR /app
RUN sudo apt-get update && sudo apt-get install python-pip && pip install -r requirements-pi.txt
ENTRYPOINT ["python", "app.py"]
