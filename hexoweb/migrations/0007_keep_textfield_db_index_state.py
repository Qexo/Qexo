# Manually generated to preserve db_index state and best-effort create indexes.
#
# Why SeparateDatabaseAndState:
# - Django state should still reflect db_index=True for these TextField columns.
# - Backends that support these indexes should keep the database-level performance
#   benefit.
# - Backends that reject TEXT/BLOB indexes (for example MySQL without key length)
#   should not fail the whole migration chain.

import logging

from django.db import migrations, models


logger = logging.getLogger(__name__)


def is_mongodb_backend(schema_editor):
    """Use the same MongoDB detection approach as migration 0006."""
    is_mongodb = (
        'mongodb' in schema_editor.connection.vendor.lower()
        if hasattr(schema_editor.connection, 'vendor')
        else False
    )

    if not is_mongodb and hasattr(schema_editor.connection, 'settings_dict'):
        engine = schema_editor.connection.settings_dict.get('ENGINE', '')
        is_mongodb = 'mongodb' in engine.lower()

    return is_mongodb


def add_text_db_indexes_if_supported(apps, schema_editor):
    from django.db.utils import DatabaseError, NotSupportedError

    if is_mongodb_backend(schema_editor):
        logger.info("Skip creating TEXT db indexes on MongoDB backend.")
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
        except (DatabaseError, NotSupportedError, NotImplementedError, AttributeError) as exc:
            # Some backends do not support indexing these TEXT/BLOB columns.
            logger.warning("Skip creating index %s on %s due to backend limitation: %s", index.name, model._meta.db_table, exc)


def remove_text_db_indexes_if_present(apps, schema_editor):
    from django.db.utils import DatabaseError, NotSupportedError

    if is_mongodb_backend(schema_editor):
        logger.info("Skip removing TEXT db indexes on MongoDB backend.")
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
        except (DatabaseError, NotSupportedError, NotImplementedError, AttributeError) as exc:
            logger.warning("Skip removing index %s on %s because it is unavailable: %s", index.name, model._meta.db_table, exc)


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
