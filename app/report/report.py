from flask import Blueprint
from flask import current_app as app


# Blueprint Configuration
report_bp = Blueprint(
    'report_bp', __name__,
    template_folder='templates',
    static_folder='static'
)