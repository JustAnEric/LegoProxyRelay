import sys, os, argparse, json
from ..main import WebSocket
from .bcolors import *

parser = argparse.ArgumentParser(description="LegoProxy Relay Command Line Tool", prog=sys.argv[0])
group = parser.add_subparsers(title='LegoProxy Relay Command Line Tool', description='Commands to manage the Relay runtime.', required=True)

rungroup = group.add_parser(name='run', help='Command to run the Relay Server.')
configgroup = group.add_parser(name='config', help='Commands to manage the Relay configuration.')

rungroup.add_argument('...', type=str, help='Do not use')
rungroup.add_argument('relay_address', type=str, help="The Proxy Address of your server, e.g. 0.0.0.0:8080/relay or 0.0.0.0:8080 or 0.0.0.0/relay")
rungroup.add_argument('relay_id', type=int, help="The Relay identifier of your client, e.g. 0")
rungroup.add_argument('--password', type=str, help="The Proxy's relay password set on your server.", required=False, default="")
rungroup.add_argument('--config', type=str, help="The JSON Relay configuration file to use.", required=False, default="")

configgroup.add_argument('...', type=str, help='Do not use')
configgroup.add_argument('config_file', type=str, help="Configuration file path.")
configgroup.add_argument('action', type=str, help="Action to induce upon the configuration.", choices=["make", "destroy"])
configgroup.add_argument('--name', type=str, help="The name of the configuration file key.", required=False, default="")
configgroup.add_argument('--value', type=str, help="The value of the configuration file key.", required=False, default="")

runargs = []
configargs = []

if sys.argv[1] == "run":
    runargs = rungroup.parse_args()
elif sys.argv[1] == "config":
    configargs = configgroup.parse_args()

if runargs != []:
    if hasattr(runargs,'relay_address'):
        if runargs.relay_address:

            wsRelay = WebSocket()

            wsRelay.start((runargs.relay_address or "0.0.0.0/relay"), (runargs.relay_id or 0), ((runargs.password if hasattr(runargs,'password') else None) or ""))

if configargs != []:
    if hasattr(configargs,'config_file'):
        if configargs.config_file:
            print("Relay Service Configuration Tool")
            
            if hasattr(configargs,'action'):
                if configargs.action == "make":
                    configuration = {
                        "relay_id": None,
                        "relay_password": None,
                        "relay_address": "0.0.0.0/relay",
                        "settings": {
                            "cache": {"enable_ttl": True, "ttl": 150, "max_size": 100}
                        }
                    }
                    print("Making configuration file at location specified...")
                    if os.path.isfile(configargs.config_file):
                        print(f"\nSorry to interrupt, but... There's already that configuration file at this location.\nWe like to do things the, ask way. Are you sure you would like to overwrite this file? {Blue}Y{NC} to overwrite, {Red}N{NC} to dismiss and quit.")
                        confirmt = input('[Y/N] ')
                        if confirmt.strip().lower() == 'y':
                            print("Overwriting...")
                            with open(configargs.config_file,'w') as f:
                                json.dump(configuration,f,indent=4)
                                f.close()
                            print(f"Configuration file location: {os.path.abspath(configargs.config_file)}")
                            exit(0)
                        else:
                            print("Dismissed.\nQuitting...")
                            exit(0)
                    elif os.path.isdir(configargs.config_file):
                        print("Writing...")
                        with open(os.path.join(configargs.config_file,'./config.json'),'w') as f:
                            json.dump(configuration,f,indent=4)
                            f.close()
                        print(f"Configuration file location: {os.path.abspath(os.path.join(configargs.config_file,'./config.json'))}")
                        exit(0)
                    else:
                        print("Writing...")
                        with open(configargs.config_file,'w') as f:
                            json.dump(configuration,f,indent=4)
                            f.close()
                        print(f"Configuration file location: {os.path.abspath(configargs.config_file)}")
                        exit(0)
                if configargs.action == "destroy":
                    if os.path.isfile(configargs.config_file):
                        print(f"\nAre you sure you would like to delete this file {Underlined}permanently{NC}? {Blue}Y{NC} to delete, {Red}N{NC} to dismiss and quit.")
                        confirmt = input('[Y/N] ')
                        if confirmt.strip().lower() == 'y':
                            print("Deleting...")
                            os.remove(configargs.config_file)
                            print("Deleted.")
                            exit(0)
                        else:
                            print("Dismissed.\nQuitting...")
                            exit(0)
                    else:
                        print(f"{Red}ERR:{NC} No such file.")
                        exit(0)