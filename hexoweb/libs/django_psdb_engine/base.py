from django.db.backends.mysql.base import DatabaseWrapper as MysqlDatabaseWrapper
from .features import DatabaseFeatures


class DatabaseWrapper(MysqlDatabaseWrapper):
    vendor = 'planetscale'
    features_class = DatabaseFeatures