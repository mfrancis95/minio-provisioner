from os import environ
from flask import *
from flask_pyoidc.provider_configuration import *
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from .minio import create_instance, get_instances

_server_name = environ.get('URL_SCHEME', 'https') + '://' + environ['SERVER_NAME']
_server_name = _server_name[:_server_name.rindex(':')]

app = Flask(__name__)
app.config.update(
    SECRET_KEY = environ['SECRET_KEY'],
    SERVER_NAME = environ['SERVER_NAME']
)
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True
app.url_map.strict_slashes = False

_config = ProviderConfiguration(
    environ['OIDC_ISSUER'],
    client_metadata = ClientMetadata(
        environ['OIDC_CLIENT_ID'], environ['OIDC_CLIENT_SECRET']
    )
)
_auth = OIDCAuthentication({'default': _config}, app)

@app.route('/create', methods = ['POST'])
@_auth.oidc_auth('default')
def create():
    error = create_instance(session['userinfo']['preferred_username'], request.form['name'], request.form['s3_access_key'], request.form['s3_secret_key'])
    if error:
        flash(error)
    return redirect('/')

@app.route('/')
@_auth.oidc_auth('default')
def index():
    return render_template(
        'index.html',
        instances = get_instances(session['userinfo']['preferred_username']),
        server_name = _server_name
    )