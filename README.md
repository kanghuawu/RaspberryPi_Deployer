# cmpe273 Project - Raspberry Pi Deployer

### Introduction

This respository is for SJSU CMPE273's project. The concept of the project is from [here](https://github.com/kanghuawu/cmpe273-spring17/blob/master/projects/project4.md).

### Requirement

* python 2.7

* paramiko (package)

### Usage

There are three types of deployer in this work: 

1. [Remote pip installer](https://github.com/kanghuawu/cmpe273-team-project/tree/master/deployer_pip): allows you to pip install package from your computer into Raspberry Pi

```sh
$ python deployer.py -h
python deployer.py 123.4.5.6:123 https://github.com/abc/abc.git

optional arguments:
  -h, --help           show this help message and exit
  --ip IP              ex: 123.4.5.6:123
  --source SOURCE      ex: https://github.com/abc/abc.git
  --username USERNAME  username
  --password PASSWORD  password

$ python deployer.py --ip 192.168.2.2:22 --source https://github.com/nqngo22/helloworld273

```

2. [Flask deployer](https://github.com/kanghuawu/cmpe273-team-project/tree/master/deployer_flask)

Deploy in debug mode

```sh
$ python deployer-flask-v2.py -h
usage: deployer-flask-v2.py [-h] [--ip IP] [--source SOURCE]
                            [--username USERNAME] [--password PASSWORD]
                            [--action {deploy,stop,delete}]

deployer.py: Input target machine ip and package git source to deploy app. ex:
"python deployer.py --action deploy --source https://github.com/Nefeldaiel
/hello-flask --ip 192.168.2.181:22 --username YOUR_USERNAME --password
YOUR_PASSWORD". Or just "python deployer.py" using default values.

optional arguments:
  -h, --help            show this help message and exit
  --ip IP               Default value: 192.168.2.2:22
  --source SOURCE       Default value: https://github.com/kanghuawu/my-test-
                        repo
  --username USERNAME   Your username in target machine. Default value: pi
  --password PASSWORD   Your password of specified username. Default value:
                        1qazxsw2
  --action {deploy,stop,delete}
                        Action with your repo on Raspberry Pi. Default value:
                        deploy

$ python deployer-flask-v2.py --source https://github.com/kanghuawu/my-test-repo --ip 192.168.2.2:22 --action deploy

$ python deployer-flask-v2.py --source https://github.com/kanghuawu/my-test-repo --ip 192.168.2.2:22 --action stop

```

Deploy in production: 

Follow following step for setting up nginx and uwsgi ([reference](http://stackoverflow.com/questions/24941791/starting-flask-server-in-background)). 

1. Install nginx and uwsgi $ sudo apt-get install nginx uwsgi uwsgi-plugin-python

2. Add socket file 

```sh
$ cd /tmp 

$ touch mysite.sock 

$ sudo chown www-data mysite.sock

```
3. Change setting for nginx 

```sh
$ cd /etc/nginx/sites-available $ sudo rm default 

$ sudo vim /etc/nginx/sites-available/mysite 

(Paste File 1 into the file) 

$ sudo ln -s /etc/nginx/sites-available/mysite /etc/nginx/sites-enabled/mysite
```

4. Add setting for uwsgi 

```sh
$ sudo vim /etc/uwsgi/apps-available/mysite.ini 

(Paste File 2 into the file. Change the home path to your own path!) 

$ sudo ln -s /etc/uwsgi/apps-available/mysite.ini /etc/uwsgi/apps-enabled/mysite.ini
```

5. Make sure your app.py is in ~/hello-flask

6. Start-up the server $ sudo service nginx restart $ sudo service uwsgi restart

7. Test your app: http://your.ip.address (port is set to 80)



File 1

```sh
server {
    listen 80;
    server_tokens off;
    location / {
         include uwsgi_params;
         uwsgi_pass unix:/tmp/mysite.sock;
     }
}
```

File 2
[uwsgi]

```sh
vhost = true
socket = /tmp/mysite.sock
chdir = /home/pi/hello-flask
module = app
callable = app
```


```sh
$ python deployer-flask.py -h
usage: deployer-flask.py [-h] [--ip IP] [--source SOURCE]
                         [--username USERNAME] [--password PASSWORD]
                         [--action ACTION]

deployer.py: Input target machine ip and package git source to deploy app. ex:
"python deployer.py --action deploy --source https://github.com/Nefeldaiel
/hello-flask --ip 192.168.2.181:22 --username YOUR_USERNAME --password
YOUR_PASSWORD". Or just "python deployer.py" using default values.

optional arguments:
  -h, --help           show this help message and exit
  --ip IP              Default value: 192.168.2.181:22
  --source SOURCE      Default value: https://github.com/Nefeldaiel/hello-
                       flask
  --username USERNAME  Your username in target machine. Default value: pi
  --password PASSWORD  Your password of specified username. Default value:
                       1qazxsw2
  --action ACTION      deploy, redeploy, stop. Default value: deploy

$ python deployer-flask.py --source https://github.com/kanghuawu/my-test-repo --ip 192.168.2.2:22 --action deploy

$ python deployer-flask.py --source https://github.com/kanghuawu/my-test-repo --ip 192.168.2.2:22 --action stop

```

3. [Docker deployer](https://github.com/kanghuawu/cmpe273-team-project/tree/master/deployer_docker)


