import paramiko
import argparse

# print "> deployer start"
default_hostname = '192.168.2.181'
default_port = '22'
default_ip = default_hostname + ":" + default_port
default_source = 'https://github.com/abc/abc.git' 
# default_source = 'https://github.com/django-extensions/django-extensions.git'
default_username = 'pi'
default_password = 'raspberry'

COMMAND_NOT_FOUND = 'command not found'
WARNING_PIP_NOT_INSTALLED = 'Error: command "pip" does not exist on target system. Abort. '
WARNING_PYTHON_NOT_INSTALLED = 'Error: command "python" does not exist on target system. Abort. '
WARNING_AUTHENTICATE_FAILURE = 'Error: Authentication failure. Wrong username/password. Abort. '

def startSshConnection():
	paramiko.util.log_to_file('paramiko.log')
	s = paramiko.SSHClient()
	s.load_system_host_keys()
	s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		s.connect(hostname, port, username, password)
	except paramiko.ssh_exception.AuthenticationException:
		print WARNING_AUTHENTICATE_FAILURE
		return None
	else:
		return s

def closeSshConnection(s):
	s.close()

def executeAndOutput(ssh, command):
	stdin, stdout, stderr = ssh.exec_command(command)
	printOutput(stdout, "stdout")
	printOutput(stderr, "stderr")

def printOutput(source, name):
	outputString = source.read().strip()
	if len(outputString) > 0:
		print outputString

def isCommandInstalled(ssh, command):
	stdin, stdout, stderr = ssh.exec_command(command)
	stdoutStr = stdout.read()
	stderrStr = stderr.read()
	if COMMAND_NOT_FOUND in stderrStr:
		return False
	else:
		return True

def deployApp(sshConn, source):
	repo = (source.split('/')[-1])[:-4]

	command = (
      'mkdir /home/pi/apps/{0} && git clone {1} /home/pi/apps/{2}'
      ' && wget https://raw.githubusercontent.com/kanghuawu/cmpe273-team-project/master/sample_apps/flask-video-streaming/Dockerfile -P /home/pi/apps/{3}'
      ' && docker build -t {4}:latest /home/pi/apps/{5}'
      ' && docker run -d -p 5000:5000 {6}'
	).format(repo, source, repo, repo, repo, repo, repo)
	executeAndOutput(sshConn, command)	
	'''
	command1 = 'mkdir /home/pi/apps/' + repo + ' && git clone ' + source + ' /home/pi/apps/' + repo
	command2 = 'wget https://raw.githubusercontent.com/kanghuawu/cmpe273-team-project/master/sample_apps/flask-video-streaming/Dockerfile -P /home/pi/apps/' + repo
	command3 = 'docker build -t ' + repo + ':latest /home/pi/apps/' + repo
	command4 = 'docker run -d -p 5000:5000 ' + repo
	executeAndOutput(sshConnection, command1)
	executeAndOutput(sshConnection, command2)
	executeAndOutput(sshConnection, command3)
	executeAndOutput(sshConnection, command4)
	'''

def generateDockerfile(sshConn, source):
	repo = (source.split('/')[-1])[:-4]
	path = ('/home/pi/apps/{0}/Dockerfile').format(repo)
	command = (
      "echo $'FROM resin/rpi-raspbian:latest\n"
      "COPY . /app\n"
      "WORKDIR /app\n"
      "RUN sudo apt-get update && sudo apt-get install python-pip && pip install -r requirements.txt\n"
      "ENTRYPOINT [\"python\", \"app.py\"]' > {0}"
  ).format(path)
	executeAndOutput(sshConn,command)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='deployer.py: Input target machine ip and package git source to deploy app. ex: "python deployer.py --ip 192.168.2.181:22 --source https://github.com/django-extensions/django-extensions.git --username YOUR_USERNAME --password YOUR_PASSWORD". Or just "python deployer.py" using default values.')
	parser.add_argument("--ip", help='Default value: ' + default_ip, default=default_ip)
	parser.add_argument("--source", help='Default value: ' + default_source, default=default_source)
	parser.add_argument("--username", help='Your username in target machine. Default value: ' + default_username, default=default_username)
	parser.add_argument("--password", help='Your password of specified username. Default value: ' + default_password, default=default_password)
	args = parser.parse_args()
	hostname = args.ip.split(":")[0]
	try:
		port = int(args.ip.split(":")[1])
	except:
		port = default_port
	source = args.source
	username = args.username
	password = args.password

	print "> Connect to " + username + ":" + password + "@" + hostname + ":" + str(port)
	# commands = 'source ~/Programming/virtualenv/env1/bin/activate\nyes | pip install git+' + source
	commands = 'yes | sudo pip install git+' + source
	# print commands
	sshConnection = startSshConnection()
	if sshConnection is not None:
		isPythonInstalled = isCommandInstalled(sshConnection, 'python --version')
		isPipInstalled = isCommandInstalled(sshConnection, 'pip --version')
		if isPythonInstalled and isPipInstalled:
			print "> Start to deploy app from: " + source
			executeAndOutput(sshConnection, commands)
			#deployApp(sshConnection,source)
			#generateDockerfile(sshConnection, source)
			closeSshConnection(sshConnection)
		elif not isPythonInstalled:
			print WARNING_PYTHON_NOT_INSTALLED
		else:
			print WARNING_PIP_NOT_INSTALLED

# print "> deployer end"
