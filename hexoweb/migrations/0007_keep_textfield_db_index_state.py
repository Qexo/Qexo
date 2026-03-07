# Manually generated to preserve db_index state and best-effort create indexes.
#
# Why SeparateDatabaseAndState:
# - Django state should still reflect db_index=True for these TextField columns.
# - Backends that support these indexes should keep the database-level performance
#   benefit.
# - Backends that reject TEXT/BLOB indexes (for example MySQL without key length)
#   should not fail the whole migration chain.

from django.db import migrations, models


def _is_mongodb_backend(schema_editor):
    vendor = getattr(schema_editor.connection, 'vendor', '')
    if 'mongodb' in vendor.lower():
        return True
    if hasattr(schema_editor.connection, 'settings_dict'):
        engine = schema_editor.connection.settings_dict.get('ENGINE', '')
        return 'mongodb' in engine.lower()
    return False


def add_text_db_indexes_if_supported(apps, schema_editor):
    from django.db.utils import DatabaseError

    if _is_mongodb_backend(schema_editor):
        return

    Cache = apps.get_model('hexoweb', 'Cache')
    CustomModel = apps.get_model('hexoweb', 'CustomModel')
    FriendModel = apps.get_model('hexoweb', 'FriendModel')
    ImageModel = apps.get_model('hexoweb', 'ImageModel')
    PostModel = apps.get_model('hexoweb', 'PostModel')
    SettingModel = apps.get_model('hexoweb', 'SettingModel')
    TalkModel = apps.get_model('hexoweb', 'TalkModel')

    indexes = [
        (Cache, models.Index(fields=['name'], name='hexoweb_cac_name_393d54_idx')),
        (CustomModel, models.Index(fields=['name'], name='hexoweb_cus_name_5ca240_idx')),
        (FriendModel, models.Index(fields=['time'], name='hexoweb_fri_time_a9636e_idx')),
        (ImageModel, models.Index(fields=['name'], name='hexoweb_ima_name_6a60d9_idx')),
        (PostModel, models.Index(fields=['path'], name='hexoweb_pos_path_3952f0_idx')),
        (SettingModel, models.Index(fields=['name'], name='hexoweb_set_name_3e7cb3_idx')),
        (TalkModel, models.Index(fields=['time'], name='hexoweb_tal_time_a7d991_idx')),
    ]

    for model, index in indexes:
        try:
            schema_editor.add_index(model, index)
        except DatabaseError:
            # Some backends do not support indexing these TEXT/BLOB columns.
            pass


def remove_text_db_indexes_if_present(apps, schema_editor):
    from django.db.utils import DatabaseError

    if _is_mongodb_backend(schema_editor):
        return

    Cache = apps.get_model('hexoweb', 'Cache')
    CustomModel = apps.get_model('hexoweb', 'CustomModel')
    FriendModel = apps.get_model('hexoweb', 'FriendModel')
    ImageModel = apps.get_model('hexoweb', 'ImageModel')
    PostModel = apps.get_model('hexoweb', 'PostModel')
    SettingModel = apps.get_model('hexoweb', 'SettingModel')
    TalkModel = apps.get_model('hexoweb', 'TalkModel')

    indexes = [
        (Cache, models.Index(fields=['name'], name='hexoweb_cac_name_393d54_idx')),
        (CustomModel, models.Index(fields=['name'], name='hexoweb_cus_name_5ca240_idx')),
        (FriendModel, models.Index(fields=['time'], name='hexoweb_fri_time_a9636e_idx')),
        (ImageModel, models.Index(fields=['name'], name='hexoweb_ima_name_6a60d9_idx')),
        (PostModel, models.Index(fields=['path'], name='hexoweb_pos_path_3952f0_idx')),
        (SettingModel, models.Index(fields=['name'], name='hexoweb_set_name_3e7cb3_idx')),
        (TalkModel, models.Index(fields=['time'], name='hexoweb_tal_time_a7d991_idx')),
    ]

    for model, index in indexes:
        try:
            schema_editor.remove_index(model, index)
        except DatabaseError:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('hexoweb', '0006_remove_duplicate_indexes_for_mongodb'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    add_text_db_indexes_if_supported,
                    remove_text_db_indexes_if_present,
                ),
            ],
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
