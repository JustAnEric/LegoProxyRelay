import websocket, time, sys, rel, json, time
from .cli import bcolors
from .logger import Logger
from httpx import Client
from shortuuid import ShortUUID

class WebSocket():
    class InternalWSEV():
        def __init__(self, app):
            self._app = app
            
        def on_open(self, ws:websocket.WebSocket):
            if self._app.logging: print("Opened Relay client successfully")
            
            ws.send(str(self._app.relay_id))
            
            self._app.connect_stage = 1
            self._app.connect_stage_data = {'password': self._app.relay_password}
            
        def on_close(self, ws:websocket.WebSocket, close_status_code, close_message):
            if self._app.logging: print("Relay connection was closed so relay service is stopping...")
            exit(0)
            
        def on_message(self, ws:websocket.WebSocket, data: str):
            if data == "true" and self._app.connect_stage == 1:
                ws.send(str(self._app.connect_stage_data.get('password')))
                self._app.connect_stage = 2
            
            if data == "false" and self._app.connect_stage == 1:
                if self._app.logging: print("Relay client has completed authentication successfully: no password")
                self._app.connect_stage = -1 # authenticated
            
            if data == "authenticated" and self._app.connect_stage == 2:
                if self._app.logging: print("Relay client has completed authentication successfully")
                self._app.connect_stage = -1 # authenticated
            
            if data == "notauthenticated" and self._app.connect_stage == 2:
                if self._app.logging: print("Relay client hasn't completed authentication: invalid relay password")
                self._app.connect_stage = -10
            
            if data.startswith('HTTP'):
                # get ready to receive the next relay message
                if self._app.logging: print("\nMessage received, beginning JSON transmission")
                
                id = data.split('HTTP ')[1]
                
                self._app.log.log_begin_json_transmission(id)
                
                #self._app.relay_accept_stage = 1
                #self._app.relay_accept_data = {'id': id}
            
            if data.startswith('{'):
                while self._app.last_request_id != None: pass
                
                #self._app.relay_accept_stage = 0
                #id = self._app.relay_accept_data['id']
                #self._app.relay_accept_data = {}
                
                d = json.loads(data)
                
                id = d.get('_id')
                
                self._app.log.log_start_request_transmission(id, d)
                
                self._app.last_request_id = id
                
                request_start_time = time.time()
                
                with Client() as cli:
                    if d['query'] == "None":
                        req = cli.build_request(d['method'], f"https://{d['api']}.roblox.com/{d['endpoint']}", json=data)
                    else:
                        req = cli.build_request(d['method'], f"https://{d['api']}.roblox.com/{d['endpoint']}?{d['query']}", json=data)

                    res = cli.send(req)
                    response = res.json()
                
                request_end_time = time.time()
                request_total_time = (request_end_time - request_start_time)
                    
                ws.send(
                    json.dumps({
                        "id": id, 
                        "response": response,
                        "type": "relay_response",
                        "request_metrics": {
                            "request_time": [request_total_time, request_start_time, request_end_time]
                        }
                    })
                )
                
                self._app.last_request_id = None
                
                self._app.log.log_finish_request_transmission_success(id, d)
            
        def on_error(self, ws:websocket.WebSocket, exception: Exception):
            if str(exception).startswith('[Errno -3] Temporary failure in name res'):
                err_request_id = self._app.last_request_id
                trace_id = ShortUUID().random(12)
                self._app.last_request_id = None
                
                self._app.log.log_websocket_request_error(trace_id, exception)
                
                ws.send(
                    json.dumps({
                        "id": err_request_id,
                        "response": {
                            "relay_error": f"This relay request ({err_request_id}) had trouble in resolution.",
                            "relay_trace_id": trace_id
                        },
                        "type": "relay_error",
                        "exception": str(exception)
                    })
                )
    
    
    def __init__(self, *, dispatcher:bool=True):
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
        self.last_request_id = None
        self.dispatcher_allowed = dispatcher
        self.wse = self.InternalWSEV(self)
        self.log = Logger(self)
        
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
        
        if self.dispatcher_allowed:
            self.websocket_client.run_forever(dispatcher=rel)
            rel.signal(2, rel.abort)  # Keyboard Interrupt
            rel.dispatch()
        else:
            self.websocket_client.run_forever()