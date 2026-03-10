import paramiko
import sys
import time
import os

host = '62.72.32.37'
user = 'root'
password = 'Aa7161062.123'

backend_repo = 'git@github.com:ACSES-corp/Scholar-Backend.git'
frontend_repo = 'git@github.com:ACSES-corp/ACSES-Scholar.git'

backend_path = '/var/www/acses_backend'
frontend_path = '/var/www/acses_scholar'

# Local paths
base_local = r'd:/Complete/ACSES Scholar/Quantum uz backend'

def run_commands(client, commands):
    for cmd in commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8', 'ignore')
        err = stderr.read().decode('utf-8', 'ignore')
        if out: print(out)
        if err: print(err, file=sys.stderr)

def upload_folder(sftp, local_dir, remote_dir):
    if not os.path.exists(local_dir):
        return
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = remote_dir + '/' + item
        if os.path.isfile(local_path):
            print(f"Uploading file: {local_path} -> {remote_path}")
            sftp.put(local_path, remote_path)
        elif os.path.isdir(local_path):
            if item == '__pycache__' or item == '.git' or item == 'venv':
                continue
            try:
                sftp.mkdir(remote_path)
            except:
                pass
            upload_folder(sftp, local_path, remote_path)

def deploy():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Connecting to {host}...")
        client.connect(host, username=user, password=password, timeout=60)
        
        # 1. System Updates
        print("System dependencies (already handled mostly, but checking)...")
        run_commands(client, [
            "apt-get update -y && apt-get install -y python3-venv python3-pip postgresql-client nginx curl git",
            "command -v node || (curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs)",
            "command -v pm2 || npm install -g pm2"
        ])

        # 2. Backend Deployment
        print("Deploying Backend...")
        run_commands(client, [
            f"mkdir -p {backend_path}",
            f"[ -d {backend_path}/.git ] || git clone {backend_repo} {backend_path}",
            f"cd {backend_path} && git pull"
        ])

        # Upload local fixes (Models, Views, Admin, Settings, etc.)
        print("Uploading local fixes to server...")
        with client.open_sftp() as sftp:
            upload_folder(sftp, os.path.join(base_local, 'application'), f"{backend_path}/application")
            upload_folder(sftp, os.path.join(base_local, 'project'), f"{backend_path}/project")

        # Setup Venv and Requirements
        run_commands(client, [
            f"cd {backend_path} && [ -d venv ] || python3 -m venv venv",
            f"cd {backend_path} && venv/bin/pip install --upgrade pip",
            f"cd {backend_path} && venv/bin/pip install -r requirements.txt gunicorn psycopg2-binary"
        ])

        # Create .env for backend
        print("Creating backend .env...")
        env_content = f"""DJANGO_SECRET_KEY=django-insecure-prod-key-7161062
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS={host},localhost,127.0.0.1
DB_NAME=acses_scholar
DB_USER=postgres
DB_PASSWORD=root123
DB_HOST=127.0.0.1
DB_PORT=5432
"""
        with client.open_sftp() as sftp:
            with sftp.file(f"{backend_path}/.env", 'w') as f:
                f.write(env_content)

        # Database creation and migration
        print("Migrating database...")
        client.exec_command("sudo -u postgres psql -c 'CREATE DATABASE acses_scholar;'")
        run_commands(client, [
            f"cd {backend_path} && venv/bin/python3 manage.py makemigrations application",
            f"cd {backend_path} && venv/bin/python3 manage.py migrate",
            f"cd {backend_path} && venv/bin/python3 manage.py collectstatic --noinput"
        ])

        # Restart Backend
        print("Starting Backend Service...")
        gunicorn_service = f"""[Unit]
Description=Gunicorn instance to serve ACSES Backend
After=network.target

[Service]
User=root
WorkingDirectory={backend_path}
ExecStart={backend_path}/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 project.wsgi:application

[Install]
WantedBy=multi-user.target
"""
        with client.open_sftp() as sftp:
            with sftp.file("/etc/systemd/system/acses_backend.service", 'w') as f:
                f.write(gunicorn_service)

        run_commands(client, [
            "systemctl daemon-reload",
            "systemctl enable acses_backend",
            "systemctl restart acses_backend"
        ])

        # 3. Frontend Deployment
        print("Deploying Frontend...")
        run_commands(client, [
            f"mkdir -p {frontend_path}",
            f"[ -d {frontend_path}/.git ] || git clone {frontend_repo} {frontend_path}",
            f"cd {frontend_path} && git pull",
            f"cd {frontend_path} && npm install"
        ])

        # Create .env.local
        frontend_env = f"NEXT_PUBLIC_BACKEND_API_URL=http://{host}/api/v1\n"
        with client.open_sftp() as sftp:
            with sftp.file(f"{frontend_path}/.env.local", 'w') as f:
                f.write(frontend_env)

        # Build and Start Frontend
        run_commands(client, [
            f"cd {frontend_path} && npm run build",
            f"cd {frontend_path} && pm2 delete acses_frontend || true",
            f"cd {frontend_path} && pm2 start npm --name acses_frontend -- start",
            "pm2 save"
        ])

        # 4. Nginx Configuration
        print("Configuring Nginx...")
        nginx_config = f"""server {{
    listen 80;
    server_name {host};

    location /api/v1/ {{
        proxy_pass http://127.0.0.1:8000/api/v1/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    location /django-admin/ {{
        proxy_pass http://127.0.0.1:8000/django-admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}

    location /static/ {{
        alias {backend_path}/static/;
    }}

    location /media/ {{
        alias {backend_path}/media/;
    }}

    location / {{
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        with client.open_sftp() as sftp:
            with sftp.file("/etc/nginx/sites-available/acses_scholar", 'w') as f:
                f.write(nginx_config)
            
        run_commands(client, [
            "ln -sf /etc/nginx/sites-available/acses_scholar /etc/nginx/sites-enabled/",
            "rm -f /etc/nginx/sites-enabled/default",
            "nginx -t",
            "systemctl restart nginx"
        ])

        print("Full Deployment completed successfully!")

    except Exception as e:
        print(f"Deployment Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy()
