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