from os_exec.linux import Linux


class Centos7(Linux):
    def __init__(self, ssh):
        super().__init__(ssh)

        stdin, stdout, stderr = self.ssh.exec_command("ls /etc/sysconfig/network-scripts/ | grep ^ifcfg-e | head -n 1")
        self.ens = stdout.read().decode().strip()
        print("\tNetwork card:", self.ens)
    
    def set_hostname(self, inputs): 
        print("\tSet Hostname: {}".format(inputs))
        self.ssh.exec_command("hostnamectl set-hostname {}".format(inputs))
    
    def set_network(self, cmd, inputs):
        stdin, stdout, stderr = self.ssh.exec_command('cat /etc/sysconfig/network-scripts/{} | grep {}'.format(self.ens, cmd))
        stdout = stdout.read().decode().strip()
        if len(stdout) > 0:
            self.ssh.exec_command('sed -i s/{}.*/{}={}/g /etc/sysconfig/network-scripts/{}'.format(cmd, cmd, inputs, self.ens))
            print("\tReplace", cmd)
        else:
            self.ssh.exec_command('echo {}={} >> /etc/sysconfig/network-scripts/{}'.format(cmd, inputs, self.ens))
            print("\tAdd", cmd)
        return super().set_network(cmd, inputs)
    
    def close(self):
        print("\tRestart Network.")
        self.ssh.exec_command("systemctl restart network")
        self.ssh.close()
