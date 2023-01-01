from django.db.backends.mysql.features import DatabaseFeatures as MysqlBaseDatabaseFeatures

class DatabaseFeatures(MysqlBaseDatabaseFeatures):
    supports_foreign_keys = False