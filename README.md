# PidogMCP - FastMCP Server for Pidog Robot API

A remote FastMCP service that wraps the **Pidog** robot API, providing a standardized Model Context Protocol (MCP) interface to control a Pidog quadruped robot remotely.

## Overview

PidogMCP is an HTTP-based MCP server that exposes the Pidog robot API through a set of tools and resources. It allows you to:

- **Execute predefined actions**: Walk, sit, stand, stretch, and 17+ other pre-programmed behaviors
- **Direct motor control**: Move legs, head, and tail to specific angles
- **Body control**: Adjust body pose and rotation in 3D space
- **Sensor access**: Read battery voltage, ultrasonic distance, and IMU data
- **Audio playback**: Play sound effects from the robot's speaker
- **Remote access**: Control the robot over HTTP from anywhere on the network

## Architecture

- **Server**: FastMCP HTTP server running on configurable host/port (default: `127.0.0.1:8080`)
- **Protocol**: Model Context Protocol (MCP) via HTTP
- **Mode**: Supports both real robot control and mock mode for testing
- **Threading**: Built-in support for concurrent robot movements (legs, head, tail independently)

## Features

### Tools (17 total)

| Tool | Description |
|------|-------------|
| `do_action` | Execute 21+ pre-programmed actions (walk, sit, etc.) |
| `move_legs` | Move legs to specific angles |
| `move_head` | Move head with yaw/roll/pitch control |
| `move_tail` | Move tail to specific angles |
| `stop_movement` | Stop all current movement |
| `wait_movement_done` | Wait for all movement to complete |
| `is_movement_done` | Check if movement is complete |
| `set_body_pose` | Set body position (x, y, z) |
| `set_body_rotation` | Set body rotation (roll, pitch, yaw) |
| `get_battery_voltage` | Read battery voltage in volts |
| `get_distance` | Read ultrasonic sensor distance in cm |
| `get_imu_data` | Read accelerometer and gyroscope data |
| `speak` | Play audio file (non-blocking) |
| `speak_block` | Play audio file (blocking until complete) |
| `reset_to_lie_position` | Stop and return to lying position |

### Resources

- `status`: Get current server and robot status

### Available Actions (21 total)

#### Body Positioning
- `stand` - Stand upright
- `sit` - Sit down
- `lie` - Lie flat on the ground
- `lie_with_hands_out` - Lie down with front legs extended
- `half_sit` - Half-sitting position

#### Movement
- `forward` - Walk forward
- `backward` - Walk backward
- `turn_left` - Turn left while moving forward
- `turn_right` - Turn right while moving forward
- `trot` - Fast trotting gait

#### Body Expressions
- `stretch` - Stretch the body
- `push_up` - Do push-ups
- `doze_off` - Doze off with nodding head

#### Head Expressions
- `nod_lethargy` - Nod head with lethargy
- `shake_head` - Shake head left and right
- `tilting_head_left` - Tilt head to the left
- `tilting_head_right` - Tilt head to the right
- `tilting_head` - Tilt head left and right repeatedly
- `head_bark` - Raise head and bark position
- `head_up_down` - Move head up and down

#### Tail Control
- `wag_tail` - Wag tail

## Requirements

- Python 3.12 or later
- `mcp[cli]>=1.26.0` - Model Context Protocol library
- `uvicorn>=0.27.0` - ASGI web server
- `pidog>=1.0.0` - Pidog robot library (optional; server runs in mock mode without it)

## Installation

### Option 1: Using UV (recommended)

```bash
# Clone or navigate to the project
cd pidogMCP

# Install dependencies using UV
uv sync

# Or install in development mode
uv pip install -e .
```

### Option 2: Using pip

```bash
pip install -e .
```

## Configuration

Configure the server using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PIDOG_MCP_HOST` | `127.0.0.1` | Server listening address |
| `PIDOG_MCP_PORT` | `8080` | Server listening port |

## Running the Server

### Option 1: Using UV

```bash
# Run the server
uv run pidogmcp
```

### Option 2: Using Python directly

```bash
# Run the server
python -m pidogmcp.server
```

### Option 3: With custom configuration

```bash
# Run on all interfaces, port 9000
PIDOG_MCP_HOST=0.0.0.0 PIDOG_MCP_PORT=9000 uv run pidogmcp
```

## Usage Examples

### Using MCP CLI

Once the server is running, you can interact with it using the MCP CLI:

```bash
# In another terminal, test the server
mcp dev http://127.0.0.1:8080

# Execute an action
> do_action "stand"
> do_action "forward" 1 75

# Check status
> status
```

### Using Python

```python
import requests

# Server URL
SERVER_URL = "http://127.0.0.1:8080"

# Execute an action
response = requests.post(
    f"{SERVER_URL}/tools/do_action",
    json={
        "action_name": "stand",
        "step_count": 1,
        "speed": 50,
        "pitch_comp": 0,
    }
)
print(response.json())

# Get battery voltage
response = requests.post(
    f"{SERVER_URL}/tools/get_battery_voltage",
    json={}
)
print(response.json())
```

### Using curl

```bash
# Execute an action
curl -X POST http://127.0.0.1:8080/tools/do_action \
  -H "Content-Type: application/json" \
  -d '{
    "action_name": "sit",
    "step_count": 1,
    "speed": 50,
    "pitch_comp": 0
  }'

# Get status
curl http://127.0.0.1:8080/resources/status
```

## Typical Workflow

```python
# 1. Make the robot stand
do_action("stand", speed=60)

# 2. Wait for movement to complete
wait_movement_done()

# 3. Walk forward 3 times
do_action("forward", step_count=3, speed=70)

# 4. Check if movement is done
while not is_movement_done():
    # Wait a bit
    time.sleep(0.1)

# 5. Make it sit
do_action("sit", speed=60)

# 6. Return to lying position
reset_to_lie_position()
```

## Mock Mode

If the Pidog robot module is not installed or not available, the server runs in **mock mode**. In this mode:

- All tools return success responses with mock data
- No actual robot hardware is required
- Perfect for testing and development
- Check the `status` resource to verify the mode

To run in mock mode:

```bash
# Install without pidog
uv sync --no-dev

# Run server
uv run pidogmcp

# Server will output: "Pidog module available: False"
```

## Architecture Details

### Threading Model

The Pidog robot supports independent concurrent movements:

- **Legs** run in their own thread (`_legs_action_thread`)
- **Head** runs in its own thread (`_head_action_thread`)
- **Tail** runs in its own thread (`_tail_action_thread`)

This allows the robot to move multiple parts simultaneously. The MCP server respects this with:

- `move_legs()`, `move_head()`, `move_tail()` - Queue movements independently
- `wait_movement_done()` - Waits for ALL movements to complete
- `is_movement_done()` - Checks status of all movements

### Error Handling

- All tools return structured responses with `status` and `message` fields
- Errors don't crash the server; they're returned as error responses
- Mock mode provides realistic error messages when the module isn't available

## Troubleshooting

### Server fails to start
- Ensure port 8080 is not in use: `netstat -an | grep 8080`
- Try a different port: `PIDOG_MCP_PORT=9000 uv run pidogmcp`

### Pidog module not found
- The server will run in mock mode (check the startup message)
- To use real robot: `pip install pidog` or `uv pip install pidog`
- Make sure you have I2C enabled on Raspberry Pi (if using hardware)

### Robot doesn't respond
- Check battery voltage: `get_battery_voltage()`
- Verify robot is powered on
- Try `reset_to_lie_position()` to recover from stuck state

### Actions not working
- Verify action name is spelled correctly (case-sensitive)
- Check the available actions list in this README
- Test with `do_action("stand")` first as a baseline

## Project Structure

```
pidogMCP/
├── pyproject.toml              # Project configuration
├── README.md                   # This file
├── pidogmcp/
│   ├── __init__.py            # Package initialization
│   └── server.py              # FastMCP server implementation
└── .venv/                     # Virtual environment (after installation)
```

## Development

### Running tests

```bash
# (Tests can be added to the project)
pytest tests/
```

### Code style

The project follows PEP 8 style guidelines. Format code with:

```bash
black pidogmcp/
```

## Performance Notes

- **Action execution**: Most actions complete in 1-5 seconds
- **Movement buffering**: Movements are queued and executed sequentially per body part
- **Sensor polling**: Distance and IMU data update every 0.01-0.05 seconds
- **Concurrent movements**: Three independent threads handle legs, head, and tail

## Security Considerations

- **Local network only**: Default configuration binds to `127.0.0.1`
- **No authentication**: This implementation does not include authentication
- **Remote access**: To expose on network, set `PIDOG_MCP_HOST=0.0.0.0` (use with caution)
- **Production deployment**: Add API key authentication if exposed remotely

## License

This project wraps the Pidog API. Refer to [pidog repository](https://github.com/sunfounder/pidog) for license information.

## References

- [Pidog Repository](https://github.com/sunfounder/pidog)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
- [FastMCP](https://github.com/jlowin/FastMCP)

## Support

For issues related to:
- **PidogMCP server**: Create an issue in this repository
- **Pidog robot API**: See [Pidog issues](https://github.com/sunfounder/pidog/issues)
- **MCP protocol**: See [MCP documentation](https://modelcontextprotocol.io)
