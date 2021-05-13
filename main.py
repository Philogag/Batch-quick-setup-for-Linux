import getopt
import sys, os
import paramiko

from os_exec import get_exec_for_os

arglist = [
    ['h'    , 'help'    , '', 'Show this help page.'],
    ['e'    , 'example' , '', 'Make a example Table.'],
    ['l:'   , 'list='   , '', ['Host list file, must the "csv" file encoding by UTF-8. ', 'Must use!', 'Use --example option to get a empty list.', 'Leave the first row as header.']],
    ['u:'   , 'user='   , 'root','User for doing Script.'],
    ['r:'   , 'rsa-key=', '~/.ssh/id_rsa',  'Rsa private key for ssh.'],
    ['p:'   , 'passwd=' , '', ['User password for ssh, use rsa first.', 'When set, ignore --rsa-key']],
]

try:
    options, args = getopt.getopt(sys.argv[1:],''.join([arg[0] for arg in arglist]),[arg[1] for arg in arglist])
except getopt.GetoptError:
    sys.exit()

optdic = {}
for arg, val in options:
    arg = arg.replace('-', '', 2)[0]
    for row in arglist:
        if arg is row[1][0]:
            optdic[arg[0]] = val

for optrow in arglist[3:]:
    if not optrow[0][0] in optdic.keys():
        optdic[optrow[0][0]] = optrow[2]  # load default args.

def printhelp():
    print("Options:")
    print("  {:<16}{:<16}{:}".format("Args:", "Default:", "   Description:"))
    for row in arglist:
        if type(row[3]) is str:
            print("  {:<4}{:<12}{:<16}{:}".format(
                '-' + row[0].replace(':', ''), 
                "--" + row[1],
                row[2], row[3]
            ))
        else:
            print("  {:<4}{:<12}{:<16}{:}".format(
                '-' + row[0].replace(':', ''), 
                "--" + row[1],
                row[2], row[3][0]
            ))
            for morerow in row[3][1:]:
                print("  {:<4}{:<12}{:<16} {:}".format(
                    '', '', '',morerow
                ))

if 'h' in optdic.keys():
    printhelp()
    sys.exit(0)

if 'e' in optdic.keys():
    print()
    printhelp()
    with open("example.csv", 'w+', encoding="utf-8") as f:
        f.write("HOST,bootproto,ipaddr,netmask,gateway,dns1,dns2,passwd,hostname\n")
    sys.exit(0)

if not 'l' in optdic.keys():
    print('You need to specify the list file by using "-l file_name" or "-list=file_name".\n')
    printhelp()
    sys.exit(0)

if not os.path.isfile(optdic['l']):
    print('The list file not found.\n')
    sys.exit(0)

with open(optdic['l'], 'r', encoding="utf-8") as f :
    rows = [r.strip().split(',') for r in f.readlines()]

if len(row) <= 2 or rows[0][0] != "HOST":
    print('No header have been found in list file.\n')
    sys.exit(0)


failed_rows = []
for r in rows[1:]:
    ssh = paramiko.client.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if 'p' in optdic.keys(): # use password
        ssh.connect(r[0], username=optdic['u'], password=optdic['p'])
    else:
        # os.path.expanduser(optdic['r'])
        ssh.connect(r[0], username=optdic['u'], key_filename=os.path.expanduser(optdic['r']))

    transport = ssh.get_transport()
    if not transport.is_active():
        print(r[0]+":", "SSH active failed.")
        failed_rows.append(r)
        continue
    if not transport.is_authenticated():
        print(r[0]+":", "SSH authenticated failed.")
        failed_rows.append(r)
        continue

    print(r[0]+":", "Start.")
    exe = get_exec_for_os(ssh)
    for arg1, arg2 in list(zip(rows[0], r))[1:]:
        if (len(arg2) > 0):
            exe.do(arg1, arg2)
    exe.close()
    print(r[0]+":", "OK.")
