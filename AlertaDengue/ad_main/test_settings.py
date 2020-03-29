from .settings import *  # noqa: F403


DATABASES['default']['TEST'] = DATABASES['default']['default']  # noqa: F405
