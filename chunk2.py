class TrailerMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        trailer_headers = [('Trailer', 'Expires')]

        def custom_start_response(status, headers, exc_info=None):
            headers += trailer_headers
            return start_response(status, headers, exc_info)

        def custom_response_generator(response):
            for data in response:
                yield data
            yield b'Expires: Wed, 21 Oct 2015 07:28:00 GMT'

        return custom_response_generator(self.app(environ, custom_start_response))

# Flask应用
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

# 包装Flask应用
app.wsgi_app = TrailerMiddleware(app.wsgi_app)

if __name__ == '__main__':
    app.run(port=8000)
