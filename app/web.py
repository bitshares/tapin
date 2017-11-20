from flask_cors import CORS
from flaskext.markdown import Markdown
from . import app, views

from .apiv2 import apiv2

# Setup CORS
cors = CORS(app, resources={r".*/api/v1/.*": {"origins": "*"}})

# Markdown for index page
markdown = Markdown(
    app,
    extensions=['meta',
                'tables'
                ],
    safe_mode=True,
    output_format='html4',
)


app.register_blueprint(apiv2, url_prefix="/api/v2")
