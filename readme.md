# How to deploy on a server

## 1. Clone the repository

```bash
cd /var/www
git clone https://github.com/muratsat/tetrus
cd tetrus
```

## 2. Setup a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Configure systemd service

Create a file `/etc/systemd/system/tetrus.service` with the following content:

```
[Unit]
Description=FastAPI Application
After=network.target

[Service]
ExecStart=/var/www/tetrus/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
WorkingDirectory=/var/www/tetrus
User=root
Restart=always

[Install]
WantedBy=multi-user.target
```

Then reload systemd daemon and start the service:

```bash
systemctl daemon-reload
systemctl start tetrus
systemctl enable tetrus
```
