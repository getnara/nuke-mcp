#!/usr/bin/env python3
import socket
import json
import sys

class FoundryNukeClient:
    def __init__(self, host='127.0.0.1', port=8765):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Connected to Foundry Nuke bridge at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Error connecting to Foundry Nuke bridge: {e}")
            return False
    
    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None
    
    def send_command(self, command_type, args=None):
        if args is None:
            args = {}
        
        if not self.socket:
            if not self.connect():
                return {"error": "Not connected to Foundry Nuke bridge"}
        
        command = {
            "type": command_type,
            "args": args
        }
        
        try:
            # Send the command
            self.socket.sendall(json.dumps(command).encode('utf-8'))
            
            # Receive the response
            response = self.socket.recv(8192).decode('utf-8')
            return json.loads(response)
        except Exception as e:
            print(f"Error sending command: {e}")
            self.disconnect()
            return {"error": str(e)}
    
    def create_node(self, node_type, name=None):
        args = {
            "nodeType": node_type
        }
        if name:
            args["name"] = name
        
        return self.send_command("createNode", args)
    
    def set_knob_value(self, node_name, knob_name, value):
        args = {
            "nodeName": node_name,
            "knobName": knob_name,
            "value": value
        }
        
        return self.send_command("setKnobValue", args)
    
    def get_node(self, node_name):
        args = {
            "nodeName": node_name
        }
        
        return self.send_command("getNode", args)
    
    def execute_render(self, write_node_name, frame_start, frame_end):
        args = {
            "writeNodeName": write_node_name,
            "frameRangeStart": frame_start,
            "frameRangeEnd": frame_end
        }
        
        return self.send_command("execute", args)

# Example usage
if __name__ == "__main__":
    client = FoundryNukeClient()
    
    if len(sys.argv) < 2:
        print("Usage: python foundry_client.py [command] [args...]")
        print("Commands:")
        print("  create [node_type] [name]")
        print("  set [node_name] [knob_name] [value]")
        print("  get [node_name]")
        print("  render [write_node_name] [frame_start] [frame_end]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) < 3:
            print("Usage: python foundry_client.py create [node_type] [name]")
            sys.exit(1)
        
        node_type = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else None
        
        result = client.create_node(node_type, name)
        print(json.dumps(result, indent=2))
    
    elif command == "set":
        if len(sys.argv) < 5:
            print("Usage: python foundry_client.py set [node_name] [knob_name] [value]")
            sys.exit(1)
        
        node_name = sys.argv[2]
        knob_name = sys.argv[3]
        value = sys.argv[4]
        
        # Try to convert value to number if it looks like one
        try:
            value = float(value)
            # Convert to int if it's a whole number
            if value.is_integer():
                value = int(value)
        except ValueError:
            pass
        
        result = client.set_knob_value(node_name, knob_name, value)
        print(json.dumps(result, indent=2))
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: python foundry_client.py get [node_name]")
            sys.exit(1)
        
        node_name = sys.argv[2]
        
        result = client.get_node(node_name)
        print(json.dumps(result, indent=2))
    
    elif command == "render":
        if len(sys.argv) < 5:
            print("Usage: python foundry_client.py render [write_node_name] [frame_start] [frame_end]")
            sys.exit(1)
        
        write_node_name = sys.argv[2]
        frame_start = int(sys.argv[3])
        frame_end = int(sys.argv[4])
        
        result = client.execute_render(write_node_name, frame_start, frame_end)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
    
    client.disconnect() 