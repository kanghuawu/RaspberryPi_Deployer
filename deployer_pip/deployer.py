import paramiko
import argparse

# print "> deployer start"
# commands = 'cd ~/Programming/DjangoTest/test/\nls'
default_hostname = '192.168.2.2'
default_port = '22'
default_ip = default_hostname + ":" + default_port
# default_source = 'https://github.com/abc/abc.git' 
default_source = 'https://github.com/django-extensions/django-extensions.git'
try:
	from account_setting import *
except ImportError:
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
	# if len(command.strip()) > 0:
	# print "$ " + command.strip()
	stdin, stdout, stderr = ssh.exec_command(command)
	printOutput(stdout, "stdout")
	printOutput(stderr, "stderr")

def printOutput(source, name):
	outputString = source.read().strip()
	if len(outputString) > 0:
		# print "- " + name
		print outputString
		# print "- end of " + name

def isCommandInstalled(ssh, command):
	stdin, stdout, stderr = ssh.exec_command(command)
	stdoutStr = stdout.read()
	stderrStr = stderr.read()
	if COMMAND_NOT_FOUND in stderrStr:
		return False
	else:
		return True

def readCommandFromFile(fileloc):
	try:
		f = open(fileloc)
		return f.readlines()
	except:
		print WARNING_COMMAND_FILE_NOT_EXISTS
		return None


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='deployer.py: Input target machine ip and package git source to deploy app. ex: python deployer.py 123.4.5.6:123 https://github.com/abc/abc.git')
	parser.add_argument("--ip", help='ex: 123.4.5.6:123', default=default_ip)
	parser.add_argument("--source", help='ex: https://github.com/abc/abc.git', default=default_source)
	parser.add_argument("--username", help='username', default=default_username)
	parser.add_argument("--password", help='password', default=default_password)
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
	commands = 'yes | sudo pip install git+' + source
	sshConnection = startSshConnection()
	if sshConnection is not None:
		print "> Start to deploy app from: " + source
		executeAndOutput(sshConnection, commands)
		closeSshConnection(sshConnection)

# print "> deployer end"
