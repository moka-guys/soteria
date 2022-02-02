from app import app

if __name__ == "__main__":
    # outputs trace to command line, should only be run like this during development
    if app.config['DEBUG']:
        app.run(host='0.0.0.0', port=3333, threaded=True)