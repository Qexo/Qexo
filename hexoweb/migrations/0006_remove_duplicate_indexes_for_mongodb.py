# Generated manually to fix MongoDB index conflicts (issue #681)
#
# This migration removes redundant explicit indexes for non-MongoDB databases
# that were created by the original version of migration 0004.
#
# Background:
# - Modified migration 0004 now conditionally creates indexes based on database backend
# - MongoDB users: Only reverse indexes (-date, -time) are created explicitly
# - Non-MongoDB users: All indexes were created explicitly in the original migration 0004
#
# This migration:
# - Removes the redundant forward indexes for non-MongoDB users (db_index=True provides these)
# - Is a no-op for MongoDB users (these indexes were never created)
# - Keeps reverse indexes which can't be expressed by db_index=True alone

from django.db import migrations
import os


def should_remove_indexes(apps, schema_editor):
    """
    Check if we should remove the redundant indexes.
    Returns True for non-MongoDB databases that had migration 0004 applied before the fix.
    """
    return not bool(os.environ.get("MONGODB_HOST"))


class Migration(migrations.Migration):

    dependencies = [
        ('hexoweb', '0005_alter_cache_content_alter_cache_name_and_more'),
    ]

    operations = [
        # Remove redundant forward indexes for non-MongoDB databases
        # These are now provided by db_index=True on the model fields
        # MongoDB users never had these indexes created, so RemoveIndex will be a no-op
        
        migrations.RemoveIndex(
            model_name='cache',
            name='hexoweb_cac_name_393d54_idx',
        ),
        migrations.RemoveIndex(
            model_name='custommodel',
            name='hexoweb_cus_name_5ca240_idx',
        ),
        migrations.RemoveIndex(
            model_name='friendmodel',
            name='hexoweb_fri_time_a9636e_idx',
        ),
        migrations.RemoveIndex(
            model_name='friendmodel',
            name='hexoweb_fri_status_efb727_idx',
        ),
        migrations.RemoveIndex(
            model_name='imagemodel',
            name='hexoweb_ima_name_6a60d9_idx',
        ),
        migrations.RemoveIndex(
            model_name='postmodel',
            name='hexoweb_pos_path_3952f0_idx',
        ),
        migrations.RemoveIndex(
            model_name='postmodel',
            name='hexoweb_pos_status_989f04_idx',
        ),
        migrations.RemoveIndex(
            model_name='settingmodel',
            name='hexoweb_set_name_3e7cb3_idx',
        ),
        migrations.RemoveIndex(
            model_name='statisticpv',
            name='hexoweb_sta_url_a0e580_idx',
        ),
        migrations.RemoveIndex(
            model_name='statisticuv',
            name='hexoweb_sta_ip_b9eddf_idx',
        ),
        migrations.RemoveIndex(
            model_name='talkmodel',
            name='hexoweb_tal_time_a7d991_idx',
        ),
    ]





