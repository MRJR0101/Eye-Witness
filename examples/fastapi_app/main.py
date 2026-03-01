from eye_witness import init
from eye_witness.integrations import install_fastapi


def create_app(app):
    init(service_name="fastapi-example", flush_on_exit=False)
    install_fastapi(app)
    return app
