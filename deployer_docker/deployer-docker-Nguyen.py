import paramiko
import argparse
# import sys

print "> deployer start"
baseFolder = '~/Programming/deployer'
default_hostname = '192.168.2.181'
default_port = '22'
default_ip = default_hostname + ":" + default_port
ACTION_DEPLOY = 'deploy'
ACTION_REDEPLOY = 'redeploy'
ACTION_STOP = 'stop'
# default_source = 'https://github.com/kanghuawu/cmpe273-spring17/tree/master/assignment1/hello-flask'
default_source = 'https://github.com/Nefeldaiel/hello-flask'
default_action = ACTION_DEPLOY
default_username = 'aaa'
default_password = 'aaa'



COMMAND_NOT_FOUND = 'command not found'
NO_SUCH_FILE_OR_DIRECTORY = 'No such file or directory'
BRANCH_UP_TO_DATE = 'Your branch is up-to-date with \'origin/master\'.'
PULL_ALREADY_UP_TO_DATE = 'Already up-to-date.'
WARNING_DOCKER_NOT_INSTALLED = 'Error: command "docker" does not exist on target system. Abort. '
WARNING_GIT_NOT_INSTALLED = 'Error: command "git" does not exist on target system. Abort. '
WARNING_AUTHENTICATE_FAILURE = 'Error: Authentication failure. Wrong username/password. Abort. '
WARNING_FAIL_TO_PARSE_FOLDER_NAME_FROM_SOURCE_URL = 'Error: Fail to parse folder name from source URL. Abort. '

def startSshConnection():
	paramiko.util.log_to_file('paramiko.log')
	s = paramiko.SSHClient()
	s.load_system_host_keys()
	s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		s.connect(hostname, int(port), username, password)
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

def getAppNameFromSourceUrl(src):
	if len(src) > 0:
		arr = src.split('/')
		return arr[len(arr)-1]
	else:
		return ''

def isFolderExists(ssh, folderName):
	stdin, stdout, stderr = ssh.exec_command('cd ' + baseFolder + '\nls ' + folderName)
	stdoutStr = stdout.read()
	stderrStr = stderr.read()
	if NO_SUCH_FILE_OR_DIRECTORY in stderrStr or NO_SUCH_FILE_OR_DIRECTORY in stdoutStr:
		return False
	else:
		return True

def isBranchUpToDate(ssh, appName):
	stdin, stdout, stderr = ssh.exec_command('cd ' + baseFolder + '/' + appName + '\ngit status')
	stdoutStr = stdout.read()
	stderrStr = stderr.read()
	if BRANCH_UP_TO_DATE in stdoutStr:
		return True
	else:
		return False

# def exitOnError(errorMessage):
# 	if errorMessage is not None:
# 		print errorMessage
# 	sys.exit()

def doRedeploy(sshConnection, appName):
	print "> start re-deploying..."
	commands = 'cd ' + baseFolder + '/' + appName + '\ngit pull'
	stdin, stdout, stderr = sshConnection.exec_command(commands)
	stdoutStr = stdout.read()
	stderrStr = stderr.read()
	if PULL_ALREADY_UP_TO_DATE in stdoutStr or PULL_ALREADY_UP_TO_DATE in stderrStr:
		print "> Source no change. Complete re-deploy."
	else:
		isPullSuccessful = isBranchUpToDate(sshConnection, appName)
		if isPullSuccessful:
			print "> Pull success!"
			doDockerStop()
			doDockerBuildAndStart()
		else:
			print "> Pull Failed!"

def doDeploy(sshConnection, appName):
	print "> start deploying..."
	commands = 'cd ' + baseFolder + '\nls -al\ngit clone ' + source
	executeAndOutput(sshConnection, commands)
	isCloneSuccessful = isFolderExists(sshConnection, appName)
	if isCloneSuccessful:
		print "> Clone success!"
		doDockerStop()
		doDockerBuildAndStart()
	else:
		print "> Clone Failed!"

def doStop(sshConnection):
	print "> Stopping..."
	doDockerStop()
	doDockerDelete()

def doNothing():
	print "> do nothing..."

def generateDockerfile(sshConn, source):
	appName = getAppNameFromSourceUrl(source)
	path = baseFolder + ('/{0}/Dockerfile').format(appName)
	command = (
      "echo $'FROM resin/rpi-raspbian:latest\n"
      "COPY . /app\n"
      "WORKDIR /app\n"
      "RUN sudo apt-get update && sudo apt-get install python-pip && pip install -r requirement.txt\n"
      "ENTRYPOINT [\"python\", \"app.py\"]' > {0}"
  ).format(path)
	executeAndOutput(sshConn,command)

def doDockerBuildAndStart():
	print "> Build docker image..."
	appName = getAppNameFromSourceUrl(source)
	generateDockerfile(sshConnection, source)
	command1 = 'docker build -t ' + appName + ':latest ' + baseFolder + '/' + appName
	command2 = 'docker run -d -p 5000:5000 ' + appName
	executeAndOutput(sshConnection, command1)
	print "> Start docker service..."
	executeAndOutput(sshConnection, command2)

def doDockerStop():
	print "> Stop docker service..."
	commandstop = ('docker stop $(docker ps -q --filter ancestor={0} )').format(appName)
	executeAndOutput(sshConnection, commandstop)

def doDockerDelete():
	print "> Delete docker image..."

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='deployer.py: Input target machine ip and package git source to deploy app. ex: "python deployer.py --action deploy --source https://github.com/Nefeldaiel/hello-flask --ip 192.168.2.181:22 --username YOUR_USERNAME --password YOUR_PASSWORD". Or just "python deployer.py" using default values.')
	parser.add_argument("--ip", help='Default value: ' + default_ip, default=default_ip)
	parser.add_argument("--source", help='Default value: ' + default_source, default=default_source)
	parser.add_argument("--username", help='Your username in target machine. Default value: ' + default_username, default=default_username)
	parser.add_argument("--password", help='Your password of specified username. Default value: ' + default_password, default=default_password)
	parser.add_argument("--action", help='deploy, redeploy, stop. Default value: ' + default_action, default=default_action)
	args = parser.parse_args()
	hostname = args.ip.split(":")[0]
	try:
		port = int(args.ip.split(":")[1])
	except:
		port = default_port
	source = args.source
	username = args.username
	password = args.password
	action = args.action

	print "> Connect to " + username + ":" + password + "@" + hostname + ":" + str(port)
	# commands = 'cd ~/Programming/deployer\nls hello-flask'
	# print commands
	sshConnection = startSshConnection()
	if sshConnection is not None:
		isDockerInstalled = isCommandInstalled(sshConnection, 'docker --version')
		isGitInstalled = isCommandInstalled(sshConnection, 'git --version')
		appName = getAppNameFromSourceUrl(source)
		if not isDockerInstalled:
			print WARNING_DOCKER_NOT_INSTALLED
		if not isGitInstalled:
			print WARNING_GIT_NOT_INSTALLED
		elif len(appName) <= 0:
			print WARNING_FAIL_TO_PARSE_FOLDER_NAME_FROM_SOURCE_URL
		else:
			isAppExist = isFolderExists(sshConnection, appName)
			if isAppExist and (action == ACTION_REDEPLOY or action == ACTION_DEPLOY):
				doRedeploy(sshConnection, appName) 
			elif action == ACTION_DEPLOY or (action == ACTION_REDEPLOY and not isAppExist):
				doDeploy(sshConnection, appName)
			elif action ==ACTION_STOP:
				doDockerStop()
			elif isAppExist:
				doStop(sshConnection)
			else:
				doNothing()
			# executeAndOutput(sshConnection, commands)
		closeSshConnection(sshConnection)

print "> deployer end"
