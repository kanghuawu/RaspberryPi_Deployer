Modifed app to run with usb webcam

includes Dockerfile for flask-video-streaming

build: docker build -t flask-video-streaming:latest .

run: docker run -d -p 5000:5000 flask-video-streaming



