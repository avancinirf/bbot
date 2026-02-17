#!/bin/sh
set -e

# Inicia o scheduler do Laravel em background
php /var/www/html/artisan schedule:work >> /var/www/html/storage/logs/scheduler.log 2>&1 &

# Executa o comando passado (apache2-foreground via CMD)
exec "$@"
