#!/usr/bin/env bash
set -euo pipefail

export APP_NAME="诊所药房药品批次与效期预警系统"
export APP_ENV="production"
export APP_SECRET_KEY="item13-clinic-pharmacy-secret"
export APP_ACCESS_TOKEN_EXPIRE_MINUTES="720"
export DATABASE_HOST="127.0.0.1"
export DATABASE_PORT="3306"
export DATABASE_USER="clinic"
export DATABASE_PASSWORD="clinic123"
export DATABASE_NAME="clinic_pharmacy"
export DATABASE_CHARSET="utf8mb4"
export EXPIRY_WARNING_DAYS="90"

if [ ! -d /var/lib/mysql/mysql ]; then
  if command -v mariadb-install-db >/dev/null 2>&1; then
    mariadb-install-db \
      --user=mysql \
      --datadir=/var/lib/mysql \
      --auth-root-authentication-method=normal \
      --skip-test-db
  else
    mysql_install_db \
      --user=mysql \
      --datadir=/var/lib/mysql \
      --auth-root-authentication-method=normal
  fi
fi

install -d -o mysql -g mysql /run/mysqld /var/lib/mysql

mariadbd \
  --user=mysql \
  --datadir=/var/lib/mysql \
  --bind-address=127.0.0.1 \
  --port=3306 \
  --socket=/run/mysqld/mysqld.sock \
  --console &
db_pid=$!

for _ in $(seq 1 60); do
  if mysqladmin ping --protocol=socket --socket=/run/mysqld/mysqld.sock --silent >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

mysql -uroot --protocol=socket --socket=/run/mysqld/mysqld.sock -e "CREATE DATABASE IF NOT EXISTS clinic_pharmacy DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -uroot --protocol=socket --socket=/run/mysqld/mysqld.sock -e "CREATE USER IF NOT EXISTS 'clinic'@'localhost' IDENTIFIED BY 'clinic123';"
mysql -uroot --protocol=socket --socket=/run/mysqld/mysqld.sock -e "CREATE USER IF NOT EXISTS 'clinic'@'127.0.0.1' IDENTIFIED BY 'clinic123';"
mysql -uroot --protocol=socket --socket=/run/mysqld/mysqld.sock -e "CREATE USER IF NOT EXISTS 'clinic'@'%' IDENTIFIED BY 'clinic123';"
mysql -uroot --protocol=socket --socket=/run/mysqld/mysqld.sock -e "GRANT ALL PRIVILEGES ON clinic_pharmacy.* TO 'clinic'@'localhost';"
mysql -uroot --protocol=socket --socket=/run/mysqld/mysqld.sock -e "GRANT ALL PRIVILEGES ON clinic_pharmacy.* TO 'clinic'@'127.0.0.1';"
mysql -uroot --protocol=socket --socket=/run/mysqld/mysqld.sock -e "GRANT ALL PRIVILEGES ON clinic_pharmacy.* TO 'clinic'@'%';"
mysql -uroot --protocol=socket --socket=/run/mysqld/mysqld.sock -e "FLUSH PRIVILEGES;"

if [ ! -f /var/lib/mysql/.item13_seeded ]; then
  mysql -uroot --protocol=socket --socket=/run/mysqld/mysqld.sock clinic_pharmacy < /app/init.sql
  touch /var/lib/mysql/.item13_seeded
fi

cd /app/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8013 &
api_pid=$!

for _ in $(seq 1 90); do
  if curl -fsS http://127.0.0.1:8013/health >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "backend ready at http://127.0.0.1:8013"
echo "frontend ready at http://127.0.0.1:3013"

nginx -g "daemon off;" &
nginx_pid=$!

cleanup() {
  kill "$nginx_pid" "$api_pid" "$db_pid" 2>/dev/null || true
}

trap cleanup INT TERM EXIT

wait -n
status=$?
cleanup
exit "$status"
