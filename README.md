# PiDog MCP - Model Context Protocol Server

A FastMCP (HTTP-based Model Context Protocol) server that wraps the [Sunfounder PiDog robot API](https://github.com/sunfounder/pidog), enabling remote control and interaction with PiDog robots through a standardized protocol.

## Overview

This project provides a remote HTTP-based MCP server that exposes the Sunfounder PiDog robot API as standardized tools and resources. It allows AI assistants and other MCP clients to control PiDog robots over the network.

### Features

- **Action Control**: Execute predefined actions (stand, walk, trot, stretch, etc.)
- **Movement Control**: Direct control of legs, head, and tail positioning
- **Body Pose Control**: Set body position and rotation
- **Sensor Access**: Read battery voltage, ultrasonic distance, and IMU data
- **Audio Playback**: Play sound files with volume control
- **Status Monitoring**: Check movement completion status
- **Mock Mode**: Server can run in mock mode when pidog module is unavailable for testing

## Available Tools

### Action Control
- **`do_action`** - Execute predefined actions on the robot
  - Valid actions: stand, sit, lie, lie_with_hands_out, forward, backward, turn_left, turn_right, trot, stretch, push_up, doze_off, nod_lethargy, shake_head, tilting_head_left, tilting_head_right, tilting_head, head_bark, wag_tail, head_up_down, half_sit
  - Supports step count, speed, and pitch compensation
  
- **`list_available_actions`** - List all available action names

### Movement Control
- **`move_legs`** - Direct control of leg angles (8 parameters for 4 legs)
- **`move_head`** - Control head position with yaw/roll/pitch angles
- **`move_tail`** - Control tail position
- **`stop_movement`** - Stop all current movements
- **`wait_movement_done`** - Block until all movements complete
- **`is_movement_done`** - Check if all movements are complete

### Body Control
- **`set_body_pose`** - Set body position (x, y, z)
- **`set_body_rotation`** - Set body rotation (roll, pitch, yaw)

### Sensors
- **`get_battery_voltage`** - Get current battery voltage
- **`get_distance`** - Get ultrasonic distance reading
- **`get_imu_data`** - Get accelerometer, gyroscope, pitch, and roll data

### Audio
- **`speak`** - Play a sound file asynchronously
- **`speak_block`** - Play a sound file and wait for completion

### Resources
- **`status`** - Get current server status

## Requirements

- Python 3.12 or later
- `mcp` library (with FastMCP support)
- `pidog` library (for hardware control) - optional
- `uvicorn` (included via mcp[cli])

## Installation

1. Clone or download this project
2. Install dependencies using `uv`:

```bash
cd pidogMCP
uv sync
```

Or with pip:

```bash
pip install -e .
```

## Running the Server

### Basic Usage

Start the server on the default port 8080:

```bash
uv run pidogmcp
```

Or:

```bash
python -m pidogmcp.server
```

### Configuration

The server can be configured using environment variables:

- `PIDOG_MCP_HOST` - Server host address (default: 127.0.0.1)
- `PIDOG_MCP_PORT` - Server port (default: 8080)

Example:

```bash
export PIDOG_MCP_HOST=0.0.0.0
export PIDOG_MCP_PORT=8080
uv run pidogmcp
```

Or on Windows PowerShell:

```powershell
$env:PIDOG_MCP_HOST="0.0.0.0"
$env:PIDOG_MCP_PORT="8080"
uv run pidogmcp
```

### Mock Mode

If the `pidog` module is not installed, the server will run in mock mode, returning simulated responses instead of controlling hardware. This is useful for testing and development:

```bash
uv run pidogmcp
# Log will show: "pidog module not available - server will run in mock mode"
```

## Usage Example

Once the server is running, you can interact with it using any MCP client. Example with curl:

```bash
# Get available actions
curl http://localhost:8080/status

# Execute an action (via MCP client)
# do_action with action_name="stand", speed=50
```

## Architecture

The server is built on:
- **FastMCP**: HTTP-based Model Context Protocol implementation
- **Uvicorn**: ASGI server for hosting the FastMCP application
- **pidog**: Sunfounder PiDog robot control library

### Request Flow

```
MCP Client
    ↓
HTTP Request (port 8080)
    ↓
FastMCP Server (app)
    ↓
Tools / Resources
    ↓
Pidog API
    ↓
Robot Hardware
```

## Supported Actions

The robot supports the following predefined actions via the `do_action` tool:

| Category | Actions |
|----------|---------|
| **Base Poses** | stand, sit, lie, lie_with_hands_out, half_sit |
| **Locomotion** | forward, backward, turn_left, turn_right, trot |
| **Movements** | stretch, push_up, doze_off, wag_tail |
| **Head** | nod_lethargy, shake_head, tilting_head_left, tilting_head_right, tilting_head, head_bark, head_up_down |

## Development

### Project Structure

```
pidogMCP/
├── pyproject.toml          # Project configuration
├── pidogmcp/
│   ├── __init__.py         # Package initialization
│   └── server.py           # FastMCP server implementation
├── README.md               # This file
└── .venv/                  # Virtual environment (created by uv)
```

### Adding New Tools

To add a new tool, add a function decorated with `@app.tool()` in `pidogmcp/server.py`:

```python
@app.tool()
def my_new_tool(param: str) -> str:
    """Tool description."""
    if not PIDOG_AVAILABLE:
        return "Mock response"
    
    try:
        pidog = get_pidog()
        # Interact with pidog
        return "Success message"
    except Exception as e:
        return f"Error: {e}"
```

### Testing

Test the server in mock mode without needing hardware:

```bash
# Install without pidog dependency
pip install mcp[cli] uvicorn

# Run server
python -m pidogmcp.server
```

## Troubleshooting

### "pidog module not available"
- The server is running in mock mode, which is fine for testing
- To use with hardware, install pidog: `pip install pidog`

### Server fails to start
- Check that port 8080 is not in use: `netstat -tuln | grep 8080` (Linux/Mac) or `netstat -ano | findstr :8080` (Windows)
- Change port: `PIDOG_MCP_PORT=8081 uv run pidogmcp`

### No response from robot
- Ensure the robot is powered on and connected
- Check that the pidog library can communicate with the hardware
- Verify battery voltage using `get_battery_voltage` tool

## Resources

- [Sunfounder PiDog GitHub](https://github.com/sunfounder/pidog)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

## License

This project is provided as-is for controlling Sunfounder PiDog robots. See LICENSE for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
