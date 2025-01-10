import os

DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql_db'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'password01'),
    'database': os.getenv('DB_NAME', 'farmadvisor'),
}
