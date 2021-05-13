
from os_exec.linux import Linux
from os_exec.centos import Centos7

def get_os_type(ssh):
    stdin, stdout, stderr = ssh.exec_command("cat /etc/os-release")
    data = stdout.read().decode().split('\n')
    dic_data = {}
    for row in data:
        if len(row) > 0:
            k, v = row.split('=')
            dic_data[k] = v.replace('"', '').strip()
    return dic_data['NAME'] + " " + dic_data['VERSION_ID']



def get_exec_for_os(ssh):
    os = get_os_type(ssh)
    if os == "Centos Linux 7":
        return Centos7(ssh)
    return Centos7(ssh)