# Configure PyMySQL to work with Django
import pymysql
pymysql.install_as_MySQLdb()

# Apply Python 3.14 compatibility patches
try:
    from . import patches
except ImportError:
    pass
