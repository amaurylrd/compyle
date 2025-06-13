from importlib.metadata import version

from compyle.celery import app as celery_app

__version__ = version(__package__)
__path__ = __import__("pkgutil").extend_path(__path__, __name__)
__all__ = ("celery_app",)
