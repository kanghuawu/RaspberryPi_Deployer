import paramiko

print "== deployer start"
hostname = '192.168.2.181'
port = 22
username = 'aaa'
password = 'aaa'
COMMAND_NOT_FOUND = 'command not found'
WARNING_PIP_NOT_INSTALLED = 'Error: command "pip" does not exist on target system. Abort. '
WARNING_PYTHON_NOT_INSTALLED = 'Error: command "python" does not exist on target system. Abort. '

def startSshConnection():
	paramiko.util.log_to_file('paramiko.log')
	s = paramiko.SSHClient()
	s.load_system_host_keys()
	s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	s.connect(hostname, port, username, password)
	return s

def closeSshConnection(s):
	s.close()

def executeAndOutput(ssh, command):
	stdin, stdout, stderr = ssh.exec_command(command)
	print "----------- stdout -----"
	print stdout.read()
	print "end of stdout"
	print "----------- stderr -----"
	print stderr.read()
	print "end of stderr"

def isCommandInstalled(ssh, command):
	stdin, stdout, stderr = ssh.exec_command(command)
	stdoutStr = stdout.read()
	stderrStr = stderr.read()
	if COMMAND_NOT_FOUND in stderrStr:
		return False
	else:
		return True


if __name__ == "__main__":
	sshConnection = startSshConnection()
	if not isCommandInstalled(sshConnection, 'python --version'):
		print WARNING_PYTHON_NOT_INSTALLED
	elif not isCommandInstalled(sshConnection, 'pip --version'):
		print WARNING_PIP_NOT_INSTALLED
	else:
		print "continue..."
	closeSshConnection(sshConnection)

print "== deployer end"
