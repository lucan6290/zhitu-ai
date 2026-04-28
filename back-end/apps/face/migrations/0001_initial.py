from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UserInfo",
            fields=[
                (
                    "user_id",
                    models.AutoField(
                        primary_key=True, serialize=False, verbose_name="用户ID"
                    ),
                ),
                (
                    "user_name",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="用户名"
                    ),
                ),
                ("user_age", models.IntegerField(default=0, verbose_name="用户年龄")),
                (
                    "user_phone",
                    models.CharField(
                        db_index=True,
                        default="",
                        max_length=20,
                        verbose_name="手机号码",
                    ),
                ),
                ("user_pwd", models.CharField(max_length=100, verbose_name="用户密码")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
            ],
            options={
                "verbose_name": "用户信息",
                "verbose_name_plural": "用户信息",
                "db_table": "user_info",
            },
        ),
    ]
