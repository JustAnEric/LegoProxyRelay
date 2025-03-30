import websocket, time, sys, rel, json
from httpx import Client

class WebSocket():
    class InternalWSEV():
        def __init__(self, app):
            self._app = app
            
        def on_open(self, ws:websocket.WebSocket):
            print("Opened Relay client successfully")
            ws.send(str(self._app.relay_id))
            self._app.connect_stage = 1
            self._app.connect_stage_data = {'password': self._app.relay_password}
            
        def on_close(self, ws:websocket.WebSocket, close_status_code, close_message):
            ...
            
        def on_message(self, ws:websocket.WebSocket, data: str):
            print(data, self._app.connect_stage)
            if data == "true" and self._app.connect_stage == 1:
                ws.send(str(self._app.connect_stage_data.get('password')))
                print(self._app.connect_stage)
                self._app.connect_stage = 2
            if data == "false" and self._app.connect_stage == 1:
                print("Relay client has completed authentication successfully: no password")
                print(self._app.connect_stage)
                self._app.connect_stage = -1 # authenticated
            if data == "authenticated" and self._app.connect_stage == 2:
                print("Relay client has completed authentication successfully")
                print(self._app.connect_stage)
                self._app.connect_stage = -1 # authenticated
            if data == "notauthenticated" and self._app.connect_stage == 2:
                print("Relay client hasn't completed authentication: invalid relay password")
                print(self._app.connect_stage)
                self._app.connect_stage = -10
            if data.startswith('HTTP'):
                # get ready to receive the next relay message
                print("Message received, beginning JSON transmission")
                id = data.split('HTTP ')[1]
                self._app.relay_accept_stage = 1
                self._app.relay_accept_data = {'id': id}
            if data.startswith('{') and self._app.relay_accept_stage == 1:
                self._app.relay_accept_stage = 0
                id = self._app.relay_accept_data['id']
                self._app.relay_accept_data = {}
                d = json.loads(data)
                with Client() as cli:
                    if d['query'] == "None":
                        req = cli.build_request(d['method'], f"https://{d['api']}.roblox.com/{d['endpoint']}", json=data)
                    else:
                        req = cli.build_request(d['method'], f"https://{d['api']}.roblox.com/{d['endpoint']}?{d['query']}", json=data)

                    res = cli.send(req)
                    response = res.json()
                ws.send(json.dumps({"id": id, "response": response}))
            ...
            
        def on_error(self, ws:websocket.WebSocket, exception: Exception):
            ...
    
    
    def __init__(self):
        self.websocket_url = "ws://websocket.example.com"
        self.relay_id = None
        self.relay_password = None
        self.websocket_client = None
        self.logging = True
        self.reconnect_delay = 5
        self.connect_stage = 0
        self.relay_accept_stage = 0
        self.relay_accept_data = {}
        self.connect_stage_data = {}
        self.wse = self.InternalWSEV(self)
        
    @property
    def x_forwarded_for(self):
        return f"relay-service-python-{self.relay_id}.local"
        
    def start(self, relay_address: str = "0.0.0.0/relay", relay_id: int = 0, relay_password: str = ""):
        """
        relay_address: The address to assign the relay to.
        relay_id: The relay ID to assign the relay to.
        """
        
        self.websocket_url = f"ws://{relay_address}"
        self.relay_id = relay_id
        self.relay_password = relay_password
        
        if self.logging: print("Starting Relay service...")
        
        #websocket.enableTrace(True)
        
        self.websocket_client = websocket.WebSocketApp(
            url = self.websocket_url,
            header = {
                'X-Forwarded-For': self.x_forwarded_for
            },
            on_open = self.wse.on_open,
            on_close = self.wse.on_close,
            on_message = self.wse.on_message,
            on_error = self.wse.on_error
        )
        
        self.websocket_client.run_forever(dispatcher=rel)
        rel.signal(2, rel.abort)  # Keyboard Interrupt
        rel.dispatch()