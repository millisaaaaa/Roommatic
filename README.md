# Roommatic

Roommatic is a Raspberry Pi based smart room management system. It integrates temperature and humidity sensing, people counting, PMV thermal comfort calculation, device control, MariaDB database storage, and a web interface.

## Project Structure

```text
Roommatic/
├── database/
│   ├── docs/
│   └── schema/
├── docs/
├── firmware/
│   └── d1_mini/
├── roomie_node/
├── scripts/
├── systemd/
├── web/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Main Components

| Component      | Description                        |
| -------------- | ---------------------------------- |
| Raspberry Pi 5 | Main controller and local server   |
| D1 mini        | DHT22 sensing and infrared control |
| DHT22          | Temperature and humidity sensor    |
| Pi Camera      | Image input for people counting    |
| YOLO           | People detection                   |
| MariaDB        | Local database                     |
| Apache / PHP   | Web interface                      |
| FastAPI        | API service                        |

## Python Environment

Create a virtual environment:

```bash
cd /home/pi/Roommatic
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If the dependency file is named `requirements.example`, rename it before use:

```bash
mv requirements.example requirements.txt
```

## Node.js Environment

Install Node.js dependencies:

```bash
cd /home/pi/Roommatic/roomie_node
npm install
```

`node_modules/` is not included in this repository.

## Database Setup

Import the latest database schema:

```bash
mysql -u roommatic_user -p roommatic < database/schema/roommatic_init_v2.sql
```

For detailed instructions, see:

```text
database/docs/database_setup.md
```

## D1 mini Setup

The D1 mini firmware should be placed in:

```text
firmware/d1_mini/d1_mini.ino
```

For upload and serial port setup, see:

```text
docs/d1_mini_setup.md
```

## Run Main Program Manually

```bash
cd /home/pi/Roommatic
source .venv/bin/activate
python -m scripts.main.main
```

## systemd Services

Roommatic uses systemd services for automatic startup.

Expected service examples:

```text
systemd/roommatic.service.example
systemd/roommatic-api.service.example
```

Check service status:

```bash
sudo systemctl status roommatic
sudo systemctl status roommatic-api
sudo systemctl status apache2
```

View logs:

```bash
journalctl -u roommatic -f
journalctl -u roommatic-api -f
```

## Files Not Included

The following files and folders should not be uploaded to GitHub:

```text
.venv/
venv/
node_modules/
__pycache__/
.env
db_connect.php
data/
logs/
```

Use `.env.example` and other `.example` files as templates for local configuration.
