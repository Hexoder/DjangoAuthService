from django.apps import apps
from django.core.exceptions import ImproperlyConfigured


def get_user_model_from_string(AUTH_USER_MODEL: str):
    try:
        app_name, model_name = AUTH_USER_MODEL.split('.')
        return apps.get_model(app_name, model_name)
    except (ValueError, LookupError) as e:
        raise ImproperlyConfigured(f"Invalid AUTH_USER_MODEL '{AUTH_USER_MODEL}': {e}")


def is_user_db_model():
    from django.apps import apps
    app_conf = apps.get_app_config('auth_service')
    USER_DB_MODEL = app_conf.USER_DB_MODEL
    return USER_DB_MODEL
