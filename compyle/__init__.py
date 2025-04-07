import pkg_resources

from compyle.celery import app as celery_app

__version__ = pkg_resources.get_distribution(__package__).version
__path__ = __import__("pkgutil").extend_path(__path__, __name__)
__all__ = ("celery_app",)
