from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0001_initial"),
    ]

    sql_operations = [
        migrations.RunSQL(
            sql=[
                (
                    "ALTER TABLE chat_session "
                    "DROP FOREIGN KEY chat_session_user_id_b860f903_fk_user_info_user_id, "
                    "ADD CONSTRAINT fk_session_user "
                    "FOREIGN KEY (user_id) REFERENCES user_info(user_id) ON DELETE CASCADE"
                ),
                (
                    "ALTER TABLE chat_message "
                    "DROP FOREIGN KEY chat_message_session_id_9abc6edf_fk_chat_session_session_id, "
                    "ADD CONSTRAINT fk_message_session "
                    "FOREIGN KEY (session_id) REFERENCES chat_session(session_id) ON DELETE CASCADE"
                ),
                (
                    "ALTER TABLE chat_message "
                    "DROP FOREIGN KEY chat_message_user_id_a47c01bb_fk_user_info_user_id, "
                    "ADD CONSTRAINT fk_message_user "
                    "FOREIGN KEY (user_id) REFERENCES user_info(user_id) ON DELETE CASCADE"
                ),
            ],
            reverse_sql=[
                (
                    "ALTER TABLE chat_session "
                    "DROP FOREIGN KEY fk_session_user, "
                    "ADD CONSTRAINT chat_session_user_id_b860f903_fk_user_info_user_id "
                    "FOREIGN KEY (user_id) REFERENCES user_info(user_id)"
                ),
                (
                    "ALTER TABLE chat_message "
                    "DROP FOREIGN KEY fk_message_session, "
                    "ADD CONSTRAINT chat_message_session_id_9abc6edf_fk_chat_session_session_id "
                    "FOREIGN KEY (session_id) REFERENCES chat_session(session_id)"
                ),
                (
                    "ALTER TABLE chat_message "
                    "DROP FOREIGN KEY fk_message_user, "
                    "ADD CONSTRAINT chat_message_user_id_a47c01bb_fk_user_info_user_id "
                    "FOREIGN KEY (user_id) REFERENCES user_info(user_id)"
                ),
            ],
        ),
    ]

    operations = sql_operations
