# Manually generated to preserve db_index state while avoiding MySQL DDL errors.
#
# Why SeparateDatabaseAndState:
# - MySQL cannot create an index directly on TEXT without key length and may fail
#   with OperationalError 1170 during online upgrade.
# - We only need to keep Django model/migration state aligned with db_index=True.
# - Database-level index DDL is intentionally skipped here.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hexoweb', '0006_remove_duplicate_indexes_for_mongodb'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='cache',
                    name='name',
                    field=models.TextField(blank=False, db_index=True),
                ),
                migrations.AlterField(
                    model_name='custommodel',
                    name='name',
                    field=models.TextField(blank=False, db_index=True),
                ),
                migrations.AlterField(
                    model_name='friendmodel',
                    name='time',
                    field=models.TextField(blank=False, db_index=True),
                ),
                migrations.AlterField(
                    model_name='imagemodel',
                    name='name',
                    field=models.TextField(blank=False, db_index=True),
                ),
                migrations.AlterField(
                    model_name='postmodel',
                    name='path',
                    field=models.TextField(blank=False, db_index=True),
                ),
                migrations.AlterField(
                    model_name='settingmodel',
                    name='name',
                    field=models.TextField(blank=False, db_index=True),
                ),
                migrations.AlterField(
                    model_name='talkmodel',
                    name='time',
                    field=models.TextField(blank=False, db_index=True),
                ),
            ],
        ),
    ]
