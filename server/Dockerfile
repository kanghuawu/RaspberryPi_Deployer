FROM resin/rpi-raspbian:latest
COPY . /app
WORKDIR /app
RUN sudo apt-get update && sudo apt-get install python-pip
ENTRYPOINT ["python", "server.py"]
