from .service import MySQLService

# Singleton service instance
mysql_service_instance = MySQLService()

# Dependency function
def get_mysql_service():
    return mysql_service_instance
