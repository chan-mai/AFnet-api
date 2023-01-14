import json

class ReturnJson():
    def err(message: str,):
        return json.dumps({'status': 'error', 'message': message},ensure_ascii = False)

    def ok(message: str, data):
        return json.dumps({'status': 'ok', 'message': message, 'data': data},ensure_ascii = False )