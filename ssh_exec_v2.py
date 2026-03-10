import paramiko
import sys
import io

def ssh_exec(host, user, password, command):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=user, password=password, timeout=30)
        
        stdin, stdout, stderr = client.exec_command(command)
        
        # Read with error handling for encoding
        out = stdout.read().decode('utf-8', errors='replace')
        err = stderr.read().decode('utf-8', errors='replace')
        
        if out:
            print(out)
        if err:
            print(err, file=sys.stderr)
        
        client.close()
    except Exception as e:
        print(f"SSH Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python ssh_exec_v2.py host user password command")
        sys.exit(1)
    
    host = sys.argv[1]
    user = sys.argv[2]
    password = sys.argv[3]
    command = " ".join(sys.argv[4:])
    
    ssh_exec(host, user, password, command)
