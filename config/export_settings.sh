DB_NAME="prestashop-db"
DB_USER="root"
DB_PASS="secureeb24p"
DB_HOST="mysql"

EXPORT_DIR="backup"
mkdir -p $EXPORT_DIR

docker exec -i $(docker-compose ps -q mysql) mysqldump -u $DB_USER -p$DB_PASS $DB_NAME > $EXPORT_DIR/db_backup.sql

echo "Export settings completed successfully."