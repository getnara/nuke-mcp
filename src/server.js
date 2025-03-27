import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';
import { exec } from 'child_process';
import { promisify } from 'util';
import net from 'net';
import path from 'path';
import { fileURLToPath } from 'url';

const execAsync = promisify(exec);

// Get the absolute path to the directory of this file
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

// TCP config to connect to foundry_nuke_bridge
const BRIDGE_HOST = '127.0.0.1';
const BRIDGE_PORT = 8765;

// Create an MCP server for Nuke
const server = new McpServer({
  name: "Nuke Bridge",
  version: "1.0.0",
  description: "MCP server for interacting with Nuke"
});

// Helper function to send commands to the foundry_nuke_bridge
async function sendToNuke(command) {
  return new Promise((resolve, reject) => {
    const client = new net.Socket();
    let data = '';

    client.connect(BRIDGE_PORT, BRIDGE_HOST, () => {
      client.write(JSON.stringify(command));
    });

    client.on('data', (chunk) => {
      data += chunk;
    });

    client.on('end', () => {
      try {
        const result = JSON.parse(data);
        resolve({
          content: [{ 
            type: "text", 
            text: JSON.stringify(result, null, 2) 
          }]
        });
      } catch (e) {
        resolve({
          content: [{ 
            type: "text", 
            text: `Error parsing response: ${data}` 
          }],
          isError: true
        });
      }
      client.destroy();
    });

    client.on('error', (err) => {
      resolve({
        content: [{ 
          type: "text", 
          text: `Connection error: ${err.message}` 
        }],
        isError: true
      });
      client.destroy();
    });
  });
}

// Create Node tool
server.tool(
  "createNode",
  {
    nodeType: z.string().describe("Type of node to create (e.g., 'Read', 'Merge2')"),
    name: z.string().optional().describe("Optional name for the node"),
    inputs: z.array(z.string()).optional().describe("Optional array of input node names")
  },
  async ({ nodeType, name, inputs }) => {
    return await sendToNuke({
      type: 'createNode',
      args: { nodeType, name, inputs }
    });
  },
  { description: "Creates a node in Nuke" }
);

// Set Knob Value tool
server.tool(
  "setKnobValue",
  {
    nodeName: z.string().describe("Name of the node"),
    knobName: z.string().describe("Name of the knob to set"),
    value: z.any().describe("Value to set the knob to (can be number, string, boolean, or array)")
  },
  async ({ nodeName, knobName, value }) => {
    return await sendToNuke({
      type: 'setKnobValue',
      args: { nodeName, knobName, value }
    });
  },
  { description: "Sets a knob value on a node" }
);

// Get Node tool
server.tool(
  "getNode",
  {
    nodeName: z.string().describe("Name of the node to get information about")
  },
  async ({ nodeName }) => {
    return await sendToNuke({
      type: 'getNode',
      args: { nodeName }
    });
  },
  { description: "Gets information about a node" }
);

// Execute tool
server.tool(
  "execute",
  {
    writeNodeName: z.string().describe("Name of the Write node to render"),
    frameRangeStart: z.number().describe("Start frame for rendering"),
    frameRangeEnd: z.number().describe("End frame for rendering")
  },
  async ({ writeNodeName, frameRangeStart, frameRangeEnd }) => {
    return await sendToNuke({
      type: 'execute',
      args: { writeNodeName, frameRangeStart, frameRangeEnd }
    });
  },
  { description: "Renders frames using a Write node" }
);

// Node Graph Management Tools

// Connect Nodes tool
server.tool(
  "connectNodes",
  {
    inputNode: z.string().describe("Name of the input node"),
    outputNode: z.string().describe("Name of the output node"),
    inputIndex: z.number().optional().describe("Input index for the connection (default is 0)")
  },
  async ({ inputNode, outputNode, inputIndex = 0 }) => {
    return await sendToNuke({
      type: 'connectNodes',
      args: { inputNode, outputNode, inputIndex }
    });
  },
  { description: "Connects nodes in the node graph" }
);

// Set Node Position tool
server.tool(
  "setNodePosition",
  {
    nodeName: z.string().describe("Name of the node"),
    xPos: z.number().describe("X position in the node graph"),
    yPos: z.number().describe("Y position in the node graph")
  },
  async ({ nodeName, xPos, yPos }) => {
    return await sendToNuke({
      type: 'setNodePosition',
      args: { nodeName, xPos, yPos }
    });
  },
  { description: "Sets the position of a node in the node graph" }
);

// Get Node Position tool
server.tool(
  "getNodePosition",
  {
    nodeName: z.string().describe("Name of the node")
  },
  async ({ nodeName }) => {
    return await sendToNuke({
      type: 'getNodePosition',
      args: { nodeName }
    });
  },
  { description: "Gets the position of a node in the node graph" }
);

// Node Group Management

// Create Group tool
server.tool(
  "createGroup",
  {
    name: z.string().optional().describe("Optional name for the group"),
    nodeNames: z.array(z.string()).optional().describe("Array of node names to include in the group")
  },
  async ({ name, nodeNames }) => {
    return await sendToNuke({
      type: 'createGroup',
      args: { name, nodeNames }
    });
  },
  { description: "Creates a group node containing the specified nodes" }
);

// Create LiveGroup tool
server.tool(
  "createLiveGroup",
  {
    name: z.string().optional().describe("Optional name for the LiveGroup"),
    nodeNames: z.array(z.string()).optional().describe("Array of node names to include in the LiveGroup"),
    filePath: z.string().optional().describe("Optional file path to save the LiveGroup")
  },
  async ({ name, nodeNames, filePath }) => {
    return await sendToNuke({
      type: 'createLiveGroup',
      args: { name, nodeNames, filePath }
    });
  },
  { description: "Creates a LiveGroup node for collaborative work" }
);

// Template and Preset Management

// Load Template tool
server.tool(
  "loadTemplate",
  {
    templateName: z.string().describe("Name of the template to load"),
    position: z.object({
      x: z.number().optional().describe("X position in node graph"),
      y: z.number().optional().describe("Y position in node graph")
    }).optional().describe("Optional position in the node graph")
  },
  async ({ templateName, position }) => {
    return await sendToNuke({
      type: 'loadTemplate',
      args: { templateName, position }
    });
  },
  { description: "Loads a Nuke template (Toolset) into the current script" }
);

// Save Template tool
server.tool(
  "saveTemplate",
  {
    templateName: z.string().describe("Name for the template"),
    nodeNames: z.array(z.string()).describe("Array of node names to include in the template"),
    category: z.string().optional().describe("Optional category for the template")
  },
  async ({ templateName, nodeNames, category }) => {
    return await sendToNuke({
      type: 'saveTemplate',
      args: { templateName, nodeNames, category }
    });
  },
  { description: "Saves selected nodes as a template (Toolset)" }
);

// Camera Tracking and 3D Tools

// Create Camera Tracker tool
server.tool(
  "createCameraTracker",
  {
    sourceName: z.string().describe("Name of the source node to track"),
    trackingFeatures: z.object({
      numberFeatures: z.number().optional().describe("Number of features to track (default is 200)"),
      featureSize: z.number().optional().describe("Size of features to track (default is 15)"),
      featureSeparation: z.number().optional().describe("Minimum separation between features (default is 20)")
    }).optional().describe("Optional tracking feature parameters")
  },
  async ({ sourceName, trackingFeatures }) => {
    return await sendToNuke({
      type: 'createCameraTracker',
      args: { sourceName, trackingFeatures }
    });
  },
  { description: "Creates and sets up a CameraTracker node" }
);

// Execute Camera Solve tool
server.tool(
  "solveCameraTrack",
  {
    cameraTrackerNode: z.string().describe("Name of the CameraTracker node"),
    solveMethod: z.enum(["Match-Moving", "Full", "Refine"]).optional().describe("Solve method (default is 'Match-Moving')")
  },
  async ({ cameraTrackerNode, solveMethod = "Match-Moving" }) => {
    return await sendToNuke({
      type: 'solveCameraTrack',
      args: { cameraTrackerNode, solveMethod }
    });
  },
  { description: "Solves a camera track using the specified CameraTracker node" }
);

// Create Scene tool
server.tool(
  "createScene",
  {
    cameraNode: z.string().optional().describe("Optional name of a camera node to include"),
    geometryNodes: z.array(z.string()).optional().describe("Optional array of geometry node names to include")
  },
  async ({ cameraNode, geometryNodes }) => {
    return await sendToNuke({
      type: 'createScene',
      args: { cameraNode, geometryNodes }
    });
  },
  { description: "Creates a 3D scene with optional camera and geometry" }
);

// Working with Deep Data

// Create Deep Nodes tool
server.tool(
  "setupDeepPipeline",
  {
    inputNodes: z.array(z.string()).describe("Array of input node names (Read nodes with Deep data)"),
    mergeOperation: z.enum(["over", "under", "plus", "difference"]).optional().describe("Merge operation (default is 'over')")
  },
  async ({ inputNodes, mergeOperation = "over" }) => {
    return await sendToNuke({
      type: 'setupDeepPipeline',
      args: { inputNodes, mergeOperation }
    });
  },
  { description: "Sets up a Deep compositing pipeline" }
);

// Batch Processing Tools

// Batch Process tool
server.tool(
  "batchProcess",
  {
    inputDirectory: z.string().describe("Directory containing input files"),
    outputDirectory: z.string().describe("Directory for output files"),
    filePattern: z.string().optional().describe("File pattern to match (e.g., '*.exr')"),
    processScript: z.string().optional().describe("Optional path to a Nuke script to process the files")
  },
  async ({ inputDirectory, outputDirectory, filePattern, processScript }) => {
    return await sendToNuke({
      type: 'batchProcess',
      args: { inputDirectory, outputDirectory, filePattern, processScript }
    });
  },
  { description: "Batch processes a directory of files using Nuke" }
);

// Script Automation Tools

// Run Python Script tool
server.tool(
  "runPythonScript",
  {
    script: z.string().describe("Python script to execute in Nuke"),
    args: z.record(z.any()).optional().describe("Optional arguments to pass to the script")
  },
  async ({ script, args }) => {
    return await sendToNuke({
      type: 'runPythonScript',
      args: { script, args }
    });
  },
  { description: "Runs a Python script in Nuke" }
);

// Load Nuke Script tool
server.tool(
  "loadScript",
  {
    filePath: z.string().describe("Path to the Nuke script file (.nk)")
  },
  async ({ filePath }) => {
    return await sendToNuke({
      type: 'loadScript',
      args: { filePath }
    });
  },
  { description: "Loads a Nuke script file" }
);

// Save Nuke Script tool
server.tool(
  "saveScript",
  {
    filePath: z.string().describe("Path to save the Nuke script file (.nk)")
  },
  async ({ filePath }) => {
    return await sendToNuke({
      type: 'saveScript',
      args: { filePath }
    });
  },
  { description: "Saves the current Nuke script to a file" }
);

// Machine Learning Tools

// Setup CopyCat tool
server.tool(
  "setupCopyCat",
  {
    trainingInputNode: z.string().describe("Name of the input node for training data"),
    trainingOutputNode: z.string().describe("Name of the output node for training data"),
    networkType: z.enum(["Basic", "UNet", "Extended"]).optional().describe("Type of neural network (default is 'Basic')")
  },
  async ({ trainingInputNode, trainingOutputNode, networkType = "Basic" }) => {
    return await sendToNuke({
      type: 'setupCopyCat',
      args: { trainingInputNode, trainingOutputNode, networkType }
    });
  },
  { description: "Sets up a CopyCat node for machine learning" }
);

// Train CopyCat Model tool
server.tool(
  "trainCopyCatModel",
  {
    copyCatNodeName: z.string().describe("Name of the CopyCat node"),
    epochs: z.number().optional().describe("Number of training epochs (default is 100)"),
    batchSize: z.number().optional().describe("Batch size for training (default is 4)")
  },
  async ({ copyCatNodeName, epochs = 100, batchSize = 4 }) => {
    return await sendToNuke({
      type: 'trainCopyCatModel',
      args: { copyCatNodeName, epochs, batchSize }
    });
  },
  { description: "Trains a CopyCat neural network model" }
);

// Common VFX Operations

// Setup Basic Comp tool
server.tool(
  "setupBasicComp",
  {
    plateNode: z.string().describe("Name of the plate node"),
    fgElements: z.array(z.string()).optional().describe("Array of foreground element node names"),
    bgElements: z.array(z.string()).optional().describe("Array of background element node names")
  },
  async ({ plateNode, fgElements, bgElements }) => {
    return await sendToNuke({
      type: 'setupBasicComp',
      args: { plateNode, fgElements, bgElements }
    });
  },
  { description: "Sets up a basic compositing tree with the provided elements" }
);

// Setup Keyer tool
server.tool(
  "setupKeyer",
  {
    inputNodeName: z.string().describe("Name of the input node to key"),
    keyerType: z.enum(["IBK", "Primatte", "Keylight", "UltraKeyer"]).optional().describe("Type of keyer to use (default is 'Primatte')"),
    screenColor: z.array(z.number()).optional().describe("Optional RGB values for the screen color")
  },
  async ({ inputNodeName, keyerType = "Primatte", screenColor }) => {
    return await sendToNuke({
      type: 'setupKeyer',
      args: { inputNodeName, keyerType, screenColor }
    });
  },
  { description: "Sets up a keying pipeline for the input node" }
);

// Setup Motion Blur tool
server.tool(
  "setupMotionBlur",
  {
    inputNodeName: z.string().describe("Name of the input node"),
    vectorNodeName: z.string().optional().describe("Optional name of a node containing motion vectors"),
    motionBlurSamples: z.number().optional().describe("Number of motion blur samples (default is 10)")
  },
  async ({ inputNodeName, vectorNodeName, motionBlurSamples = 10 }) => {
    return await sendToNuke({
      type: 'setupMotionBlur',
      args: { inputNodeName, vectorNodeName, motionBlurSamples }
    });
  },
  { description: "Sets up motion blur for the input node" }
);

// Project Management Tools

// Set Project Settings tool
server.tool(
  "setProjectSettings",
  {
    frameRange: z.object({
      first: z.number().describe("First frame of the project"),
      last: z.number().describe("Last frame of the project")
    }).optional().describe("Frame range for the project"),
    resolution: z.object({
      width: z.number().describe("Width in pixels"),
      height: z.number().describe("Height in pixels")
    }).optional().describe("Resolution of the project"),
    fps: z.number().optional().describe("Frames per second")
  },
  async ({ frameRange, resolution, fps }) => {
    return await sendToNuke({
      type: 'setProjectSettings',
      args: { frameRange, resolution, fps }
    });
  },
  { description: "Sets project settings like frame range, resolution and FPS" }
);

// List Nodes tool
server.tool(
  "listNodes",
  {
    filter: z.string().optional().describe("Optional filter to narrow down the list of nodes (e.g., 'Read')")
  },
  async ({ filter }) => {
    return await sendToNuke({
      type: 'listNodes',
      args: { filter }
    });
  },
  { description: "Lists all nodes in the current script, optionally filtered by type" }
);

export { server };
