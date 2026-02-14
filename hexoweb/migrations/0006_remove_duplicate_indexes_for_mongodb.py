# Generated manually to fix MongoDB index conflicts (issue #681)
#
# This migration removes redundant explicit indexes for non-MongoDB databases.
#
# Context:
# - Modified migration 0004 conditionally creates indexes based on database backend
# - Non-MongoDB: Creates all 14 explicit indexes
# - MongoDB: Creates only 3 reverse indexes (forward ones from db_index=True)
#
# This migration removes the 11 redundant forward indexes for non-MongoDB users.
# For MongoDB users, this is a complete no-op since those indexes never existed.

from django.db import migrations, models


def remove_redundant_indexes_if_needed(apps, schema_editor):
    """
    Remove redundant forward indexes only for non-MongoDB databases.
    MongoDB users never had these indexes, so we skip the removal entirely.
    """
    from django.db.utils import ProgrammingError, OperationalError
    
    # Check if MongoDB is being used by examining the actual database connection
    # This is more reliable than checking environment variables and works with
    # both environment-based and local config.py deployments
    is_mongodb = 'mongodb' in schema_editor.connection.vendor.lower() if hasattr(schema_editor.connection, 'vendor') else False
    
    # Fallback check for edge cases where vendor is not set
    if not is_mongodb and hasattr(schema_editor.connection, 'settings_dict'):
        engine = schema_editor.connection.settings_dict.get('ENGINE', '')
        is_mongodb = 'mongodb' in engine.lower()
    
    if is_mongodb:
        # MongoDB users never had these forward indexes created
        # Skip all RemoveIndex operations
        return
    
    # For non-MongoDB databases, remove the redundant forward indexes
    # Get model metadata
    Cache = apps.get_model('hexoweb', 'Cache')
    CustomModel = apps.get_model('hexoweb', 'CustomModel')
    FriendModel = apps.get_model('hexoweb', 'FriendModel')
    ImageModel = apps.get_model('hexoweb', 'ImageModel')
    PostModel = apps.get_model('hexoweb', 'PostModel')
    SettingModel = apps.get_model('hexoweb', 'SettingModel')
    StatisticPV = apps.get_model('hexoweb', 'StatisticPV')
    StatisticUV = apps.get_model('hexoweb', 'StatisticUV')
    TalkModel = apps.get_model('hexoweb', 'TalkModel')
    
    # List of (model, index_name, fields) to remove
    # We need to construct index objects since historical models don't have current Meta.indexes
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
    
    # Remove each index by constructing the index object
    for model, index_name, fields in indexes_to_remove:
        try:
            # Construct the index object with the expected name and fields
            index = models.Index(fields=fields, name=index_name)
            schema_editor.remove_index(model, index)
        except (ProgrammingError, OperationalError):
            # Index might not exist, already removed, or database-specific error
            # This is acceptable - we just want to ensure it's not there
            pass


def reverse_noop(apps, schema_editor):
    """No-op reverse migration"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('hexoweb', '0005_alter_cache_content_alter_cache_name_and_more'),
    ]

    operations = [
        # Use RunPython to conditionally remove indexes only for non-MongoDB
        migrations.RunPython(
            remove_redundant_indexes_if_needed,
            reverse_noop,
        ),
    ]



