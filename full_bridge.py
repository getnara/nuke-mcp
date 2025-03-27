import sys
import os

# Define the base scripts directory
SCRIPTS_BASE_DIR = 'path/to/nuke-mcp'

# Add the scripts directory to Python path
sys.path.append(SCRIPTS_BASE_DIR)

# Create directory for bridge scripts if it doesn't exist
script_dir = os.path.join(os.path.expanduser("~"), ".nuke", "scripts")
if not os.path.exists(script_dir):
    os.makedirs(script_dir)

# Copy the provided bridge scripts to the .nuke/scripts directory
with open(os.path.join(script_dir, "nuke_bridge_enhanced.py"), "w") as f:
    with open(os.path.join(SCRIPTS_BASE_DIR, 'nuke_bridge_enhanced.py'), 'r') as src:
        f.write(src.read())

with open(os.path.join(script_dir, "nuke_bridge_vfx.py"), "w") as f:
    with open(os.path.join(SCRIPTS_BASE_DIR, 'nuke_bridge_vfx.py'), 'r') as src:
        f.write(src.read())

with open(os.path.join(script_dir, "nuke_bridge_server.py"), "w") as f:
    with open(os.path.join(SCRIPTS_BASE_DIR, 'nuke_bridge_server.py'), 'r') as src:
        f.write(src.read())

# First import each module
try:
    import nuke_bridge_enhanced
    import nuke_bridge_vfx
    import nuke_bridge_server
    print("Bridge modules imported")
except ImportError as e:
    print(f"Error importing bridge modules: {e}")

# Add the scripts directory to Python path
sys.path.append(script_dir)

# Now stop any existing server
try:
    nuke_bridge_server.stop_nuke_bridge_server()
    print("Stopped existing server")
except:
    print("No existing server to stop")

# Reload all modules
import importlib
try:
    importlib.reload(nuke_bridge_enhanced)
    importlib.reload(nuke_bridge_vfx)
    importlib.reload(nuke_bridge_server)
    print("Bridge modules reloaded")
except Exception as e:
    print(f"Error reloading modules: {e}")

# Start the server
try:
    nuke_bridge_server.start_nuke_bridge_server()
    print("Started Nuke Bridge Server")
except Exception as e:
    print(f"Error starting server: {e}")

print("=" * 50)
print("Nuke MCP Bridge fully loaded and running!")
print("=" * 50)