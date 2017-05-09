import paramiko
import argparse

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
		s.connect(hostname, port, username, password)
	except paramiko.ssh_exception.AuthenticationException:
		exitOnError(WARNING_AUTHENTICATE_FAILURE)
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

def exitOnError(errorMessage):
	if errorMessage is not None:
		print errorMessage
        exit()

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

def doDockerBuildAndStart():
	commands = 'docker build -t ' + source + ' .'
	print "> Build docker image..."
	executeAndOutput(sshConnection, commands)
	print "> Start docker service..."
	commands = 'docker run -d -p 5000:5000 ' + source
	executeAndOutput(sshConnection, commands)

def doDockerStop():
	commands = 'docker stop ' + source
	print "> Stop docker service..."
	executeAndOutput(sshConnection, commands)

def doDockerDelete():
	commands = 'docker rm ' + source
	print "> Delete docker image..."
	executeAndOutput(sshConnection, commands)

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

	sshConnection = startSshConnection()
	if sshConnection is not None:
		isDockerInstalled = isCommandInstalled(sshConnection, 'docker --version')
		isGitInstalled = isCommandInstalled(sshConnection, 'git --version')
		appName = getAppNameFromSourceUrl(source)
		if not isDockerInstalled:
			exitOnError(WARNING_DOCKER_NOT_INSTALLED)
		if not isGitInstalled:
			exitOnError(WARNING_GIT_NOT_INSTALLED)
		elif len(appName) <= 0:
			exitOnError(WARNING_FAIL_TO_PARSE_FOLDER_NAME_FROM_SOURCE_URL)
		else:
			isAppExist = isFolderExists(sshConnection, appName)
			if isAppExist and (action == ACTION_REDEPLOY or action == ACTION_DEPLOY):
				doRedeploy(sshConnection, appName)
			elif action == ACTION_DEPLOY or (action == ACTION_REDEPLOY and not isAppExist):
				doDeploy(sshConnection, appName)
			elif isAppExist:
				doStop(sshConnection)
			else:
				doNothing()

		closeSshConnection(sshConnection)

print "> deployer end"
