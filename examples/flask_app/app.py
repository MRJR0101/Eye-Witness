from eye_witness import init
from eye_witness.integrations import install_flask


def configure_app(app):
    init(service_name="flask-example", flush_on_exit=False)
    install_flask(app)
    return app
