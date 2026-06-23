# Database Setup

Roommatic uses MariaDB to store user data, room data, sensor records, device information, and infrared control codes.

## Database Schema

The latest schema file is:

```text
database/schema/roommatic_init_v2.sql
```

This version includes the original Roommatic tables and the device-related tables:

```text
appliance_catalog
room_appliances
device_ir_codes
```

## Create Database

Log in to MariaDB:

```bash
sudo mariadb
```

Create the database:

```sql
CREATE DATABASE roommatic CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Create a database user:

```sql
CREATE USER 'roommatic_user'@'localhost' IDENTIFIED BY 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON roommatic.* TO 'roommatic_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Replace `YOUR_PASSWORD` with your own password.

## Import Schema

Import the Roommatic database schema:

```bash
mysql -u roommatic_user -p roommatic < database/schema/roommatic_init_v2.sql
```

## Main Tables

| Table               | Description                                                       |
| ------------------- | ----------------------------------------------------------------- |
| `users`             | User account data                                                 |
| `org`               | Organization data                                                 |
| `user_org`          | Relationship between users and organizations                      |
| `plans`             | Subscription plan data                                            |
| `rooms`             | Room information                                                  |
| `updates`           | Sensor records, PMV, PPD, and device status                       |
| `appliance_catalog` | Device catalog, including category, brand, model, and rated power |
| `room_appliances`   | Devices installed in each room                                    |
| `device_ir_codes`   | Infrared control codes for room devices                           |

## Configuration Notes

Do not upload real database passwords to GitHub.

Use example files for public release:

```text
.env.example
web/php/db_connect.example.php
```

The real files should be created locally:

```text
.env
web/php/db_connect.php
```

If the main program writes data to `room_id = 1`, make sure the `rooms` table contains a room with `room_id = 1`.

