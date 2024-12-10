DB_NAME="prestashop-db"
DB_USER="root"
DB_PASS="secureeb24p"
DB_HOST="mysql"

EXPORT_DIR="backup"

docker exec -i $(docker-compose ps -q mysql) mysql -u $DB_USER -p$DB_PASS $DB_NAME < $EXPORT_DIR/db_backup.sql

cp $EXPORT_DIR/* config/

echo "Restore settings completed successfully."