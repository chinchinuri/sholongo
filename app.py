from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__)

@app.route('/redirects', methods=['GET'])
def get_redirects():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    try:
        current_url = url
        redirects = []
        errors = []

        while True:
            try:
                response = requests.get(current_url, allow_redirects=False)
                if 300 <= response.status_code < 400:
                    new_url = response.headers.get('Location')
                    if new_url:
                        if not new_url.startswith('http'):
                            new_url = requests.compat.urljoin(current_url, new_url)
                        redirects.append(new_url)
                        current_url = new_url
                    else:
                        errors.append({"url": current_url, "error": "Missing Location header"})
                        break
                else:
                    break
            except Exception as e:
                errors.append({"url": current_url, "error": str(e)})
                break

        return jsonify({"redirects": redirects, "errors": errors})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('public', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
