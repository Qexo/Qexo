# Generated manually to fix MongoDB index conflicts (issue #681)
#
# This migration removes redundant explicit forward indexes that were created
# by earlier versions of migration 0004 for non-MongoDB databases.
#
# This migration uses a DB-only cleanup operation:
# 1. Conditionally remove indexes from the database (only for non-MongoDB)
# 2. Keep migration state unchanged to stay consistent with current 0004 state
#
# For MongoDB users, this is a complete no-op (indexes were never created).

from django.db import migrations, models


def remove_redundant_indexes_if_needed(apps, schema_editor):
    """
    Remove redundant forward indexes only for non-MongoDB databases.
    These were created by earlier versions of migration 0004.
    """
    from django.db.utils import ProgrammingError, OperationalError
    
    # Check if MongoDB is being used
    is_mongodb = 'mongodb' in schema_editor.connection.vendor.lower() if hasattr(schema_editor.connection, 'vendor') else False
    
    if not is_mongodb and hasattr(schema_editor.connection, 'settings_dict'):
        engine = schema_editor.connection.settings_dict.get('ENGINE', '')
        is_mongodb = 'mongodb' in engine.lower()
    
    if is_mongodb:
        # MongoDB users never had these indexes created
        return
    
    # Get models
    Cache = apps.get_model('hexoweb', 'Cache')
    CustomModel = apps.get_model('hexoweb', 'CustomModel')
    FriendModel = apps.get_model('hexoweb', 'FriendModel')
    ImageModel = apps.get_model('hexoweb', 'ImageModel')
    PostModel = apps.get_model('hexoweb', 'PostModel')
    SettingModel = apps.get_model('hexoweb', 'SettingModel')
    StatisticPV = apps.get_model('hexoweb', 'StatisticPV')
    StatisticUV = apps.get_model('hexoweb', 'StatisticUV')
    TalkModel = apps.get_model('hexoweb', 'TalkModel')
    
    # List of indexes to remove
    indexes_to_remove = [
        (Cache, 'hexoweb_cac_name_393d54_idx', ['name']),
        (CustomModel, 'hexoweb_cus_name_5ca240_idx', ['name']),
        (FriendModel, 'hexoweb_fri_time_a9636e_idx', ['time']),
        (FriendModel, 'hexoweb_fri_status_efb727_idx', ['status']),
        (ImageModel, 'hexoweb_ima_name_6a60d9_idx', ['name']),
        (PostModel, 'hexoweb_pos_path_3952f0_idx', ['path']),
        (PostModel, 'hexoweb_pos_status_989f04_idx', ['status']),
        (SettingModel, 'hexoweb_set_name_3e7cb3_idx', ['name']),
        (StatisticPV, 'hexoweb_sta_url_a0e580_idx', ['url']),
        (StatisticUV, 'hexoweb_sta_ip_b9eddf_idx', ['ip']),
        (TalkModel, 'hexoweb_tal_time_a7d991_idx', ['time']),
    ]
    
    # Remove each index
    for model, index_name, fields in indexes_to_remove:
        try:
            index = models.Index(fields=fields, name=index_name)
            schema_editor.remove_index(model, index)
        except (ProgrammingError, OperationalError):
            # Index might not exist
            pass


def reverse_noop(apps, schema_editor):
    """No-op reverse migration"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('hexoweb', '0005_alter_cache_content_alter_cache_name_and_more'),
    ]

    operations = [
        migrations.RunPython(
            remove_redundant_indexes_if_needed,
            reverse_noop,
        ),
    ]



