import paramiko
import sys

def ssh_exec(host, user, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password)
    stdin, stdout, stderr = client.exec_command(command, get_pty=True)
    # Print incrementally to avoid buffer issues
    for line in stdout:
        sys.stdout.write(line)
    for line in stderr:
        sys.stderr.write(line)
    client.close()

if __name__ == "__main__":
    ssh_exec(sys.argv[1], sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]))
