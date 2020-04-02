from src.webapp.app import app

PORT = 5000
HOST = '0.0.0.0'
app.run(host=HOST, port=PORT, debug=True, threaded=True)

# To run this locally:
# gunicorn -c gunicorn.conf.py wsgi:webapp
