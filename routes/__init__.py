from .analytics import create_analytics_blueprint
from .chat import create_chat_blueprint
from .pages import create_pages_blueprint
from .products import create_products_blueprint
from .users import create_users_blueprint


def register_routes(app, services):
    app.register_blueprint(create_pages_blueprint())
    app.register_blueprint(create_chat_blueprint(services))
    app.register_blueprint(create_products_blueprint(services))
    app.register_blueprint(create_users_blueprint(services))
    app.register_blueprint(create_analytics_blueprint(services))
