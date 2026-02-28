from flask import Flask, Response
import time

app = Flask(__name__)

@app.after_request
def remove_header(response):
    response.headers.pop('Content-Length', None);
    print("heee");
    return response

@app.route('/chunked')
def chunked_response():
    def generate_chunks():
        for i in range(5):
            yield f"Chunk {i}\n"
            time.sleep(1)  # 模拟耗时操作
        yield "0\r\nExpires: Wed, 21 Oct 2015 07:28:00 GMT"

    buf = '''7\r\nMozilla\r\n9\r\nDeveloper\r\n7\r\nNetwork\r\n0\r\n\r\n'''
    #response = make_response(buf);
    headers = {
            "Trailers": "Expires",
            "Content-Type": "text/plain",
            }
    #return Response(buf, headers=headers)
    return Response(generate_chunks(), headers=headers)

if __name__ == '__main__':
    app.run(port=8000, debug=True)