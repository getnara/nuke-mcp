#!/usr/bin/env python
# Bridge for communicating with Foundry's Nuke (not the folder deletion package)
import os
import socket
import threading
import json
import sys
import nuke
import nukescripts

# This script must be loaded within Foundry's Nuke application
# We use a different module name to avoid confusion with any folder deletion tool
try:
    # This import will only work when running inside Foundry's Nuke
    import nukescripts
    # Reference to the actual Foundry Nuke module 
    # (using a different name to avoid confusion with any deletion package)
    from nuke import *  # Import Nuke's contents but avoid the name conflict
    print("Successfully connected to Foundry's Nuke")
except ImportError:
    print("ERROR: This script must be run from within Foundry Nuke's Python environment.")
    print("Run this script from the Script Editor inside Foundry Nuke.")
    sys.exit(1)

# Create a TCP server to receive commands
class FoundryNukeBridge(threading.Thread):
    def __init__(self, host='127.0.0.1', port=8765):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = False
    
    def run(self):
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        self.running = True
        print(f"[FoundryNukeBridge] Server started on {self.host}:{self.port}")
        
        while self.running:
            try:
                client, address = self.server.accept()
                print(f"[FoundryNukeBridge] Client connected: {address}")
                
                # Handle client in a separate thread
                client_thread = threading.Thread(target=self.handle_client, args=(client,))
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"[FoundryNukeBridge] Error accepting connection: {e}")
    
    def handle_client(self, client):
        try:
            while self.running:
                data = client.recv(4096)
                if not data:
                    break
                
                try:
                    # Parse the command
                    print(f"[FoundryNukeBridge] Received data: {data.decode('utf-8')}")
                    command = json.loads(data.decode('utf-8'))
                    result = self.process_command(command)
                    print(f"[FoundryNukeBridge] Sending response: {json.dumps(result)}")
                    
                    # Send the result back
                    response = json.dumps(result).encode('utf-8')
                    client.sendall(response)
                    
                except json.JSONDecodeError as e:
                    error_response = json.dumps({"error": f"Invalid JSON: {str(e)}"}).encode('utf-8')
                    client.sendall(error_response)
                except Exception as e:
                    error_response = json.dumps({"error": str(e)}).encode('utf-8')
                    client.sendall(error_response)
        
        except Exception as e:
            print(f"[FoundryNukeBridge] Client handling error: {e}")
        finally:
            print("[FoundryNukeBridge] Client disconnected")
            client.close()
    
    def process_command(self, command):
        print(f"[FoundryNukeBridge] Processing command: {command}")
        cmd_type = command.get('type')
        args = command.get('args', {})
        
        if cmd_type == 'createNode':
            return self.create_node(args)
        elif cmd_type == 'setKnobValue':
            return self.set_knob_value(args)
        elif cmd_type == 'getNode':
            return self.get_node(args)
        elif cmd_type == 'execute':
            return self.execute_render(args)
        else:
            return {"error": f"Unknown command type: {cmd_type}"}
    
    def create_node(self, args):
        try:
            node_type = args.get('nodeType')
            name = args.get('name')
            
            if not node_type:
                return {"error": "nodeType is required"}
            
            # This needs to run in the main thread
            def _create():
                try:
                    if name:
                        node = nuke.createNode(node_type, f"name {name}")
                    else:
                        node = nuke.createNode(node_type)
                    return {"success": True, "name": node.name(), "type": node_type}
                except Exception as e:
                    return {"error": f"Failed to create node: {str(e)}"}
            
            result = nuke.executeInMainThread(_create)
            if result is None:
                result = {"success": True, "message": "Node created successfully"}
            print(f"[FoundryNukeBridge] Create node result: {result}")
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def set_knob_value(self, args):
        try:
            node_name = args.get('nodeName')
            knob_name = args.get('knobName')
            value = args.get('value')
            
            if not node_name:
                return {"error": "nodeName is required"}
            if not knob_name:
                return {"error": "knobName is required"}
            if value is None:
                return {"error": "value is required"}
            
            def _set_value():
                try:
                    node = nuke.toNode(node_name)
                    if not node:
                        return {"error": f"Node '{node_name}' not found"}
                    
                    knob = node.knob(knob_name)
                    if not knob:
                        return {"error": f"Knob '{knob_name}' not found on node '{node_name}'"}
                    
                    knob.setValue(value)
                    return {"success": True, "node": node_name, "knob": knob_name, "value": value}
                except Exception as e:
                    return {"error": f"Failed to set knob value: {str(e)}"}
            
            result = nuke.executeInMainThread(_set_value)
            print(f"[FoundryNukeBridge] Set knob result: {result}")
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_node(self, args):
        try:
            node_name = args.get('nodeName')
            
            if not node_name:
                return {"error": "nodeName is required"}
            
            def _get_node():
                try:
                    node = nuke.toNode(node_name)
                    if not node:
                        return {"error": f"Node '{node_name}' not found"}
                    
                    # Get basic node info
                    info = {
                        "success": True,
                        "name": node.name(),
                        "type": node.Class(),
                        "knobs": {}
                    }
                    
                    # Get knob values
                    for k in node.knobs():
                        knob = node.knob(k)
                        if knob.visible():
                            try:
                                info["knobs"][k] = knob.value()
                            except:
                                info["knobs"][k] = str(knob)
                    
                    return info
                except Exception as e:
                    return {"error": f"Failed to get node info: {str(e)}"}
            
            result = nuke.executeInMainThread(_get_node)
            if result is None:
                result = {"error": "Failed to get node info"}
            print(f"[FoundryNukeBridge] Get node result: {result}")
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def execute_render(self, args):
        try:
            write_node_name = args.get('writeNodeName')
            frame_range_start = args.get('frameRangeStart')
            frame_range_end = args.get('frameRangeEnd')
            
            if not write_node_name:
                return {"error": "writeNodeName is required"}
            if frame_range_start is None:
                return {"error": "frameRangeStart is required"}
            if frame_range_end is None:
                return {"error": "frameRangeEnd is required"}
            
            def _execute():
                try:
                    write_node = nuke.toNode(write_node_name)
                    if not write_node:
                        return {"error": f"Write node '{write_node_name}' not found"}
                    
                    if write_node.Class() != "Write":
                        return {"error": f"Node '{write_node_name}' is not a Write node"}
                    
                    nuke.execute(write_node_name, int(frame_range_start), int(frame_range_end))
                    return {
                        "success": True,
                        "writeNode": write_node_name,
                        "frameRange": {"start": frame_range_start, "end": frame_range_end}
                    }
                except Exception as e:
                    return {"error": f"Failed to execute render: {str(e)}"}
            
            result = nuke.executeInMainThread(_execute)
            print(f"[FoundryNukeBridge] Execute result: {result}")
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def stop(self):
        self.running = False
        try:
            # Connect to ourselves to break the accept() call
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.port))
            self.server.close()
        except:
            pass

# Global server instance
_foundry_bridge = None

def start_foundry_bridge():
    global _foundry_bridge
    if _foundry_bridge is None or not _foundry_bridge.running:
        _foundry_bridge = FoundryNukeBridge()
        _foundry_bridge.daemon = True
        _foundry_bridge.start()
        
        # Add a menu command to stop the server
        toolbar = nuke.menu('Nuke')
        m = toolbar.addMenu('FoundryBridge')
        m.addCommand('Stop Bridge Server', 'stop_foundry_bridge()')
        
        return True
    return False

def stop_foundry_bridge():
    global _foundry_bridge
    if _foundry_bridge and _foundry_bridge.running:
        _foundry_bridge.stop()
        _foundry_bridge = None
        return True
    return False

# Auto-start the server when this module is imported
start_foundry_bridge()

# Print success message
print("=" * 50)
print("Foundry Nuke Bridge is now running on port 8765")
print("You can now connect to Foundry Nuke via TCP at 127.0.0.1:8765")
print("=" * 50) 