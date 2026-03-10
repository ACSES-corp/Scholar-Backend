import paramiko
import sys

host = '62.72.32.37'
user = 'root'
password = 'Aa7161062.123'

def test():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Connecting to {host}...")
        client.connect(host, username=user, password=password, timeout=10)
        print("Connected!")
        stdin, stdout, stderr = client.exec_command("uptime")
        print(stdout.read().decode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    test()
