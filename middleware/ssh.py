import paramiko
import os
from scp import SCPClient

class ssh:
    '''
    A simple class around a basic paramiko ssh connection to make things easier
    to understand.
    '''

    def __init__(self, hostname, username, port, debug=True):
        '''
        Create an SSHClient object, load host keys from the known_hosts file,
        so this is only posix compliant I think.
        Setting the missing host keys policy to auto add will do nothing at
        present, but should update known_hosts in future if we come across a
        hostname that has never been connected to before. Currently that will
        cause a failure which is not handled.
        '''
        if debug:
            os.makedirs(os.path.dirname('.logs/ssh.log'), exist_ok=True)
            paramiko.util.log_to_file('.logs/ssh.log')
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname, port=port, username=username,
                            look_for_keys=True)

    def pass_command(self, command):
        '''
        Run a bash command on the remote machine and return stdout as a string.
        No error handling, stderr is ignored.
        '''
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode("utf-8")

    def secure_copy(self, filename, destination_path):
        with SCPClient(self.client.get_transport()) as scp:
            scp.put(filename, destination_path)

    def close_connection(self):
        '''
        Belt and braces method to close the client connection. Shouldnt be
        needed as exec_command should kill the connection on completion.
        '''
        self.client.close()
