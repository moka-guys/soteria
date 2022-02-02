from app import app

if __name__ == "__main__":
    from waitress import serve
    # If set to debug mode, outputs trace to command line, else runs in production mode
    if app.config['DEBUG']:
         app.run(host='0.0.0.0', port=3333, threaded=True)
    else:
         serve(app, host='0.0.0.0', port=3333)