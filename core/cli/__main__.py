import sys, os, argparse
from ..main import WebSocket

parser = argparse.ArgumentParser(description="LegoProxy Relay Command Line Tool", prog=sys.argv[0])

parser.add_argument('relay_address', type=str, help="The Proxy Address of your server, e.g. 0.0.0.0:8080/relay or 0.0.0.0:8080 or 0.0.0.0/relay")
parser.add_argument('relay_id', type=int, help="The Relay identifier of your client, e.g. 0", default=0)
parser.add_argument('--password', type=str, help="The Proxy's relay password set on your server.", required=False, default="")
# parser.add_argument('--greeting', type=str, default="Hello", help="the greeting to use")

args = parser.parse_args()

if args.relay_address:

    wsRelay = WebSocket()

    wsRelay.start((args.relay_address or "0.0.0.0/relay"), (args.relay_id or 0), ((args.password if hasattr(args,'password') else None) or ""))