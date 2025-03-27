# Nuke MCP (Model Context Protocol) Bridge

A comprehensive bridge for automating VFX workflows in Foundry's Nuke using the Model Context Protocol.

## Overview

This project provides an enhanced MCP server implementation that connects to Foundry's Nuke compositing software, enabling comprehensive automation of VFX workflows. It expands on the basic functionality of creating and manipulating nodes by adding tools for camera tracking, deep compositing, template management, machine learning, and common VFX operations.

## Features

- Node creation and manipulation
- Node graph management
- Group and LiveGroup creation
- Template/Toolset management
- Camera tracking and 3D scene setup
- Deep compositing pipelines
- Batch processing
- Machine learning with CopyCat
- Common VFX operations (keying, motion blur, etc.)
- Script management

## Requirements

- Foundry's Nuke 13.0 or later
- Node.js 14.0 or later
- Python 3.6 or later

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/nuke-mcp.git
cd nuke-mcp
```

2. Install dependencies:
```bash
npm install
```

3. Set up the bridge in Nuke:
   - Change the SCRIPTS_BASE_DIR to the location of the nuke-mcp project
   - Copy the contents od full_bridge.py and paste in nuke script editor and run it
## Starting the MCP Server

```bash
npm start
```

## Using the Bridge

Once the server is running, you can interact with Nuke using the MCP tools. Here's an example using the `createNode` tool:

```javascript
const result = await mcp.createNode({
  nodeType: "Blur",
  name: "BlurNode1"
});
```

## Available Tools

### Basic Node Operations

#### createNode
Creates a node in Nuke.
```javascript
mcp.createNode({
  nodeType: "Blur",
  name: "BlurNode1",
  inputs: ["Read1"]
});
```

#### setKnobValue
Sets a knob value on a node.
```javascript
mcp.setKnobValue({
  nodeName: "BlurNode1",
  knobName: "size",
  value: 5.5
});
```

#### getNode
Gets information about a node.
```javascript
mcp.getNode({
  nodeName: "BlurNode1"
});
```

#### execute
Renders frames using a Write node.
```javascript
mcp.execute({
  writeNodeName: "Write1",
  frameRangeStart: 1,
  frameRangeEnd: 100
});
```

### Node Graph Management

#### connectNodes
Connects nodes in the node graph.
```javascript
mcp.connectNodes({
  inputNode: "Read1",
  outputNode: "Blur1",
  inputIndex: 0
});
```

#### setNodePosition
Sets the position of a node in the node graph.
```javascript
mcp.setNodePosition({
  nodeName: "Blur1",
  xPos: 100,
  yPos: 200
});
```

#### getNodePosition
Gets the position of a node in the node graph.
```javascript
mcp.getNodePosition({
  nodeName: "Blur1"
});
```

### Group Management

#### createGroup
Creates a group node containing the specified nodes.
```javascript
mcp.createGroup({
  name: "BlurGroup",
  nodeNames: ["Blur1", "Grade1"]
});
```

#### createLiveGroup
Creates a LiveGroup node for collaborative work.
```javascript
mcp.createLiveGroup({
  name: "CompositeGroup",
  nodeNames: ["Merge1", "Grade1", "ColorCorrect1"],
  filePath: "/path/to/save/livegroup.nk"
});
```

### Template and Preset Management

#### loadTemplate
Loads a Nuke template (Toolset) into the current script.
```javascript
mcp.loadTemplate({
  templateName: "LensFlare",
  position: {
    x: 500,
    y: 300
  }
});
```

#### saveTemplate
Saves selected nodes as a template (Toolset).
```javascript
mcp.saveTemplate({
  templateName: "MyKeyer",
  nodeNames: ["Primatte1", "EdgeBlur1", "Premult1"],
  category: "Keying"
});
```

### Camera Tracking and 3D Tools

#### createCameraTracker
Creates and sets up a CameraTracker node.
```javascript
mcp.createCameraTracker({
  sourceName: "Read1",
  trackingFeatures: {
    numberFeatures: 200,
    featureSize: 15,
    featureSeparation: 20
  }
});
```

#### solveCameraTrack
Solves a camera track using the specified CameraTracker node.
```javascript
mcp.solveCameraTrack({
  cameraTrackerNode: "CameraTracker1",
  solveMethod: "Match-Moving"
});
```

#### createScene
Creates a 3D scene with optional camera and geometry.
```javascript
mcp.createScene({
  cameraNode: "Camera1",
  geometryNodes: ["Sphere1", "Card1"]
});
```

### Deep Compositing

#### setupDeepPipeline
Sets up a Deep compositing pipeline.
```javascript
mcp.setupDeepPipeline({
  inputNodes: ["Read1", "Read2", "Read3"],
  mergeOperation: "over"
});
```

### Batch Processing

#### batchProcess
Batch processes a directory of files using Nuke.
```javascript
mcp.batchProcess({
  inputDirectory: "/path/to/input",
  outputDirectory: "/path/to/output",
  filePattern: "*.exr",
  processScript: "/path/to/process.nk"
});
```

### Script Automation

#### runPythonScript
Runs a Python script in Nuke.
```javascript
mcp.runPythonScript({
  script: "nuke.nodes.Blur(size=5)",
  args: {
    blurSize: 5
  }
});
```

#### loadScript
Loads a Nuke script file.
```javascript
mcp.loadScript({
  filePath: "/path/to/script.nk"
});
```

#### saveScript
Saves the current Nuke script to a file.
```javascript
mcp.saveScript({
  filePath: "/path/to/save/script.nk"
});
```

### Machine Learning Tools

#### setupCopyCat
Sets up a CopyCat node for machine learning.
```javascript
mcp.setupCopyCat({
  trainingInputNode: "Read1",
  trainingOutputNode: "Read2",
  networkType: "UNet"
});
```

#### trainCopyCatModel
Trains a CopyCat neural network model.
```javascript
mcp.trainCopyCatModel({
  copyCatNodeName: "CopyCat1",
  epochs: 200,
  batchSize: 8
});
```

### Common VFX Operations

#### setupBasicComp
Sets up a basic compositing tree with the provided elements.
```javascript
mcp.setupBasicComp({
  plateNode: "Read1",
  fgElements: ["Read2", "Read3"],
  bgElements: ["Read4"]
});
```

#### setupKeyer
Sets up a keying pipeline for the input node.
```javascript
mcp.setupKeyer({
  inputNodeName: "Read1",
  keyerType: "Primatte",
  screenColor: [0, 0.7, 0]
});
```

#### setupMotionBlur
Sets up motion blur for the input node.
```javascript
mcp.setupMotionBlur({
  inputNodeName: "Read1",
  vectorNodeName: "VectorGenerator1",
  motionBlurSamples: 15
});
```

### Project Management

#### setProjectSettings
Sets project settings like frame range, resolution and FPS.
```javascript
mcp.setProjectSettings({
  frameRange: {
    first: 1001,
    last: 1100
  },
  resolution: {
    width: 1920,
    height: 1080
  },
  fps: 24
});
```

#### listNodes
Lists all nodes in the current script, optionally filtered by type.
```javascript
mcp.listNodes({
  filter: "Read"
});
```

## Integration with AI Assistants

This MCP implementation is designed to work seamlessly with AI assistants like Claude or GPT, allowing them to automate complex VFX tasks through natural language instructions. The comprehensive set of tools enables AI assistants to:

1. Set up complete compositing workflows
2. Create and manage templates for common operations
3. Execute camera tracking and 3D integration tasks
4. Implement sophisticated deep compositing pipelines
5. Train and apply machine learning models for automated effects

## Advanced Workflows

### Template-Based Shot Setup

```javascript
// Load a template for a standard shot
await mcp.loadTemplate({
  templateName: "StandardShotSetup",
  position: { x: 0, y: 0 }
});

// Set the plate
await mcp.setKnobValue({
  nodeName: "ReadPlate",
  knobName: "file",
  value: "/path/to/plate.####.exr"
});

// Configure shot-specific parameters
await mcp.setKnobValue({
  nodeName: "ColorCorrect1",
  knobName: "gamma",
  value: 0.9
});
```

### Automated Camera Tracking Pipeline

```javascript
// Create a read node for the plate
const readResult = await mcp.createNode({
  nodeType: "Read",
  name: "Plate"
});

// Set up the file path
await mcp.setKnobValue({
  nodeName: "Plate",
  knobName: "file",
  value: "/path/to/tracking_plate.####.exr"
});

// Create and set up the camera tracker
await mcp.createCameraTracker({
  sourceName: "Plate",
  trackingFeatures: {
    numberFeatures: 300,
    featureSize: 12
  }
});

// Solve the camera
await mcp.solveCameraTrack({
  cameraTrackerNode: "CameraTracker1",
  solveMethod: "Full"
});

// Create a 3D scene with the solved camera
await mcp.createScene({
  cameraNode: "Camera1"
});
```

## Troubleshooting

If you encounter issues with the bridge:

1. Make sure Nuke is running and the bridge script is loaded
2. Check that the TCP port (8765) is not in use by another application
3. Check the Nuke script editor for any Python errors
4. Make sure your `nuke_bridge_server.py` is properly loaded in your Nuke's initialization scripts

## License

MIT

## Credits

Developed by [Your Name/Organization]