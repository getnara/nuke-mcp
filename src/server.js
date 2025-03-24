import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
    import { z } from 'zod';
    import { exec } from 'child_process';
    import { promisify } from 'util';

    const execAsync = promisify(exec);

    // Create an MCP server for Nuke
    const server = new McpServer({
      name: "Nuke Bridge",
      version: "1.0.0",
      description: "MCP server for interacting with Nuke"
    });

    // Helper function to execute Python bridge script
    async function executeBridge(command, args = {}) {
      try {
        // Convert args to JSON string and escape quotes for command line
        const argsJson = JSON.stringify(args).replace(/"/g, '\\"');
        const { stdout, stderr } = await execAsync(`python nuke_bridge.py ${command} "${argsJson}"`);
        
        if (stderr) {
          console.error(`Bridge script error: ${stderr}`);
          return {
            content: [{ type: "text", text: `Error: ${stderr}` }],
            isError: true
          };
        }
        
        try {
          const result = JSON.parse(stdout);
          if (result.error) {
            return {
              content: [{ type: "text", text: `Error: ${result.error}` }],
              isError: true
            };
          }
          return {
            content: [{ type: "text", text: JSON.stringify(result, null, 2) }]
          };
        } catch (parseError) {
          console.error(`Error parsing bridge output: ${parseError.message}`);
          return {
            content: [{ type: "text", text: `Error parsing bridge output: ${parseError.message}\nRaw output: ${stdout}` }],
            isError: true
          };
        }
      } catch (error) {
        console.error(`Error executing bridge script: ${error.message}`);
        return {
          content: [{ type: "text", text: `Error executing bridge script: ${error.message}` }],
          isError: true
        };
      }
    }

    // 1. createNode tool
    server.tool(
      "createNode",
      {
        nodeType: z.string().describe("Type of node to create (e.g., 'Read', 'Merge2')"),
        name: z.string().optional().describe("Optional name for the node"),
        inputs: z.array(z.string()).optional().describe("Optional array of input node names")
      },
      async ({ nodeType, name, inputs }) => {
        return await executeBridge("createNode", { nodeType, name, inputs });
      },
      { description: "Creates a node of the specified type in a Nuke script" }
    );

    // 2. setKnobValue tool
    server.tool(
      "setKnobValue",
      {
        nodeName: z.string().describe("Name of the node"),
        knobName: z.string().describe("Name of the knob to set"),
        value: z.union([z.string(), z.number()]).describe("Value to set the knob to")
      },
      async ({ nodeName, knobName, value }) => {
        return await executeBridge("setKnobValue", { nodeName, knobName, value });
      },
      { description: "Sets a knob on the specified node to the provided value" }
    );

    // 3. getNode tool
    server.tool(
      "getNode",
      {
        nodeName: z.string().describe("Name of the node to get information about")
      },
      async ({ nodeName }) => {
        return await executeBridge("getNode", { nodeName });
      },
      { description: "Returns basic info about a node (type, knob values, etc.)" }
    );

    // 4. execute tool
    server.tool(
      "execute",
      {
        writeNodeName: z.string().describe("Name of the Write node to render"),
        frameRangeStart: z.number().describe("Start frame for rendering"),
        frameRangeEnd: z.number().describe("End frame for rendering")
      },
      async ({ writeNodeName, frameRangeStart, frameRangeEnd }) => {
        return await executeBridge("execute", { writeNodeName, frameRangeStart, frameRangeEnd });
      },
      { description: "Renders the specified Write node from start to end frames" }
    );

    export { server };
