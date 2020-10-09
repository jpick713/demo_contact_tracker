from flask import Blueprint
from flask import current_app as app


# Blueprint Configuration
admins_bp = Blueprint(
    'admins_bp', __name__,
    template_folder='templates',
    static_folder='static'
)