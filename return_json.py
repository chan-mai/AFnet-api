import json

class ReturnJson():
    def err(message: str,):
        return json.dumps({'status': 'error', 'message': msg})

    def ok(message: str, data):
        return json.dumps({'status': 'ok', 'message': msg, 'data': data})