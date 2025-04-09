
def is_user_db_model():
    from django.apps import apps
    app_conf = apps.get_app_config('auth_service')
    USER_DB_MODEL = app_conf.USER_DB_MODEL
    return USER_DB_MODEL
