from flask_app import app
from echo_dash_app import app as app1
from jitter_dash_app import app as app2


if __name__ == '__main__':
    app.run_server(debug=True)