from flask_sock import Sock

class LogStreamer:
    def __init__(self):
        self.clients = []

    def register(self, ws):
        self.clients.append(ws)
        while True:
            msg = ws.receive()
            if msg is None:
                break

    def write(self, text):
        for ws in list(self.clients):
            try:
                ws.send(text)
            except:
                self.clients.remove(ws)

log = LogStreamer()
