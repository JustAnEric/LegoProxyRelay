import sys, os
from ..main import WebSocket

wsRelay = WebSocket()

wsRelay.start("0.0.0.0:5200/relay", 0, "test123")