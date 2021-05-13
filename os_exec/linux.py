from os_exec.sha512 import sha512crypt, randsalt
from abc import ABCMeta, abstractmethod

class LinuxABC(metaclass=ABCMeta):
    def __init__(self, ssh):
        super().__init__()
        self.ssh = ssh;

    def do(self, command, inputs):
        if command in ["passwd"]:
            self.set_passwd(inputs)
        elif command in ["hostname"]:
            self.set_hostname(inputs)  
        else:
            self.set_network(command.upper(), inputs)
    
    @abstractmethod
    def set_passwd(self, input):
        pass
    @abstractmethod
    def set_hostname(self, input):
        pass
    @abstractmethod
    def set_network(self, cmd, input): # for all network settings
        pass

    @abstractmethod 
    def close(self): # do some thing before close ssh, like restart network.
        pass

class Linux(LinuxABC):
    def __init__(self, ssh):
        super().__init__(ssh)
    
    def set_passwd(self, inputs):
        username, passwd = inputs.split(' ');
        salted = sha512crypt(passwd.encode(), randsalt())
        print("\tSet {}'s passwd.".format(username))
        print("\tPasswd after hash:", salted)
        self.ssh.exec_command("sed -r -i s@{}:[^:]*@'{}:{}'@g /etc/shadow".format(username, username, salted.replace("@","\\@")))

    def close(self):
        self.ssh.close()