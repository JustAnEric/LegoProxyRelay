from .cli import bcolors

class Logger:
    def __init__(self, app):
        self._app = app
        
    def log_websocket_request_error(self, trace_id, exception):
        print(f"{bcolors.BckgrRed}⌊↳{bcolors.NC} {bcolors.Underlined+bcolors.LightPurple}{trace_id}{bcolors.NC}  {bcolors.Red}ERR{bcolors.NC} {exception}")
        
    def log_begin_json_transmission(self, request_id):
        print(f"{bcolors.BckgrBlue}⌈↳{bcolors.NC} {request_id} HTTP")
    
    def log_start_request_transmission(self, request_id, d):
        print(f"| ({request_id}) {bcolors.Blink}{bcolors.DarkGray}=->{bcolors.NC} {d['method']} https://{d['api']}.roblox.com/{d['endpoint']}{'?{}'.format(d['query']) if d['query'] != "None" else '?'} {bcolors.Red}x{bcolors.NC}{bcolors.Blink}{bcolors.Green}>{bcolors.NC} {self._app.websocket_url}")
    
    def log_finish_request_transmission_success(self, request_id, d):
        print(f"| ({request_id}) {bcolors.Green}<->{bcolors.NC} {d['method']} https://{d['api']}.roblox.com/{d['endpoint']}{'?{}'.format(d['query']) if d['query'] != "None" else '?'} {bcolors.Yellow}={bcolors.NC}{bcolors.Green}>{bcolors.NC} {self._app.websocket_url}")