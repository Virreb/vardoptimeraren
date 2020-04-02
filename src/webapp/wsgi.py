from src.webapp.dash_app import app

PORT = 5000
HOST = '0.0.0.0'
app.secret_key = "SuPerUltrAsaFeKey3000"     # should be set in env, but YOLO

if __name__ == '__main__':
    app.run_server(host=HOST, port=PORT, debug=True)    # if run manually, start the app
else:
    server = app.server     # for gunicorn, dont start the app, let the workers

# To run this locally:
# gunicorn -c gunicorn.conf.py wsgi:webapp

# or for easy debugging:
# python wsgi.py
