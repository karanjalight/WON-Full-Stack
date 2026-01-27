sudo -u postgres psql

CREATE DATABASE won;

CREATE USER wonuser WITH PASSWORD 'password';

ALTER ROLE wonuser SET client_encoding TO 'utf8';
ALTER ROLE wonuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE wonuser SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE won TO wonuser;

ALTER DATABASE won OWNER TO wonuser;


mkdir ~/myprojectdir
cd ~/

gunicorn --bind 0.0.0.0:8000 won.wsgi



[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=sammy
Group=www-data
WorkingDirectory=/home/won/Won-Full-Stack
ExecStart=/home//won/Won-Full-Stack/myprojectenv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          myproject.wsgi:application

[Install]
WantedBy=multi-user.target