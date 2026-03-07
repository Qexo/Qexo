# Generated manually to preserve model db_index metadata without MySQL DDL changes

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
                    field=models.TextField(db_index=True),
                ),
                migrations.AlterField(
                    model_name='custommodel',
                    name='name',
                    field=models.TextField(db_index=True),
                ),
                migrations.AlterField(
                    model_name='friendmodel',
                    name='time',
                    field=models.TextField(db_index=True),
                ),
                migrations.AlterField(
                    model_name='imagemodel',
                    name='name',
                    field=models.TextField(db_index=True),
                ),
                migrations.AlterField(
                    model_name='postmodel',
                    name='path',
                    field=models.TextField(db_index=True),
                ),
                migrations.AlterField(
                    model_name='settingmodel',
                    name='name',
                    field=models.TextField(db_index=True),
                ),
                migrations.AlterField(
                    model_name='talkmodel',
                    name='time',
                    field=models.TextField(db_index=True),
                ),
            ],
        ),
    ]
