from eye_witness import init
from eye_witness.integrations import install_celery


def configure_worker():
    init(service_name="celery-example", flush_on_exit=False)
    install_celery()
