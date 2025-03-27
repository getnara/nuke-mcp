#!/usr/bin/env python
import sys
import json
import traceback
import os

# The actual Nuke module - this should be imported when run inside Nuke
try:
    import nuke
    print("Successfully imported nuke module")
except ImportError as e:
    print(f"Error: Could not import nuke module: {e}", file=sys.stderr)
    print(f"Current PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}", file=sys.stderr)
    print(f"Script location: {os.path.abspath(__file__)}", file=sys.stderr)
    sys.exit(1)

def create_node(args):
    """Create a node in Nuke"""
    try:
        node_type = args.get('nodeType')
        name = args.get('name')
        inputs = args.get('inputs', [])
        
        if not node_type:
            return {"error": "nodeType is required"}
        
        # Create the node
        if name:
            node = nuke.createNode(node_type, f"name {name}")
        else:
            node = nuke.createNode(node_type)
        
        # Connect inputs if provided
        for i, input_name in enumerate(inputs):
            input_node = nuke.toNode(input_name)
            if input_node:
                node.setInput(i, input_node)
            else:
                return {"error": f"Input node '{input_name}' not found"}
        
        return {
            "success": True,
            "node": {
                "name": node.name(),
                "type": node_type
            }
        }
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

def set_knob_value(args):
    """Set a knob value on a node"""
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
        
        # Get the node
        node = nuke.toNode(node_name)
        if not node:
            return {"error": f"Node '{node_name}' not found"}
        
        # Set the knob value
        knob = node.knob(knob_name)
        if not knob:
            return {"error": f"Knob '{knob_name}' not found on node '{node_name}'"}
            
        knob.setValue(value)
        
        return {
            "success": True,
            "node": node_name,
            "knob": knob_name,
            "value": value
        }
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

def get_node(args):
    """Get information about a node"""
    try:
        node_name = args.get('nodeName')
        
        if not node_name:
            return {"error": "nodeName is required"}
        
        # Get the node
        node = nuke.toNode(node_name)
        if not node:
            return {"error": f"Node '{node_name}' not found"}
        
        # Gather basic information about the node
        knob_dict = {}
        for k in node.knobs():
            knob = node.knob(k)
            if knob.visible():
                try:
                    knob_dict[k] = knob.value()
                except:
                    knob_dict[k] = str(knob)
        
        return {
            "success": True,
            "node": {
                "name": node.name(),
                "type": node.Class(),
                "knobs": knob_dict
            }
        }
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

def execute_render(args):
    """Execute a render using a Write node"""
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
        
        # Get the Write node
        write_node = nuke.toNode(write_node_name)
        if not write_node:
            return {"error": f"Write node '{write_node_name}' not found"}
        
        # Check if it's a Write node
        if write_node.Class() != "Write":
            return {"error": f"Node '{write_node_name}' is not a Write node"}
        
        # Execute the render
        nuke.execute(write_node_name, int(frame_range_start), int(frame_range_end))
        
        return {
            "success": True,
            "writeNode": write_node_name,
            "frameRange": {
                "start": frame_range_start,
                "end": frame_range_end
            }
        }
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

def main():
    """Main entry point for the bridge script"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command specified"}))
        return
    
    command = sys.argv[1]
    
    # Parse arguments
    args = {}
    if len(sys.argv) > 2:
        try:
            args = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON arguments"}))
            return
    
    # Execute the appropriate command
    if command == "createNode":
        result = create_node(args)
    elif command == "setKnobValue":
        result = set_knob_value(args)
    elif command == "getNode":
        result = get_node(args)
    elif command == "execute":
        result = execute_render(args)
    else:
        result = {"error": f"Unknown command: {command}"}
    
    # Print the result as JSON
    print(json.dumps(result))

if __name__ == "__main__":
    main()
