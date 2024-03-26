from django.apps import AppConfig


class DjangolangchainappConfig(AppConfig):
    """
    Config for DjangoLangChainApp Django app.

    Sets the default primary key type to BigAutoField
    and sets the name of the app to DjangoLangChainApp
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'DjangoLangChainApp'
