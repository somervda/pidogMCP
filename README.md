# PiDog MCP Server

An [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that wraps the [Sunfounder PiDog](https://github.com/sunfounder/pidog) robot API, allowing AI assistants and MCP clients to control a PiDog quadruped robot via standardized tool calls.

## What It Does

This server exposes the PiDog robot's capabilities as MCP tools, enabling an AI assistant to:

- **Execute predefined actions** — sit, stand, lie down, walk, trot, stretch, push-up, and more
- **Control individual body parts** — legs, head, and tail servos with raw angle commands
- **Read sensor data** — battery voltage, ultrasonic distance, IMU (accelerometer/gyroscope)
- **Play sounds** — trigger sound effects through the robot's speaker
- **Control RGB LED** — set color and breathing mode for the LED strip
- **Adjust settings** — servo speeds, body height

## Available Tools

| Tool | Description |
|------|-------------|
| `do_action` | Execute a predefined robot action (see list below) |
| `get_battery_voltage` | Get the current battery voltage in volts |
| `get_distance` | Read the ultrasonic distance sensor (cm) |
| `get_imu_data` | Get IMU acceleration and gyroscope readings |
| `set_legs_speed` | Set leg servo speed (0–100) |
| `set_head_speed` | Set head servo speed (0–100) |
| `set_tail_speed` | Set tail servo speed (0–100) |
| `set_body_height` | Set body height (20–95) |
| `stop_robot` | Stop all movements and return to lying position |
| `play_sound` | Play a sound effect (e.g., "pant", "bark") |
| `set_rgb_color` | Set RGB LED color and mode |
| `direct_legs_move` | Move legs to specific servo angles |
| `direct_head_move` | Move head to specific yaw/roll/pitch angles |
| `direct_tail_move` | Move tail to a specific angle |
| `reset_robot` | Reset robot to initial position and close threads |
| `list_actions` | List all available actions with descriptions |

### Predefined Actions (`do_action`)

| Action | Description |
|--------|-------------|
| `stand` | Stand up on all four legs |
| `sit` | Sit down |
| `lie` | Lie down (doggy position) |
| `lie_with_hands_out` | Lie down with front paws extended |
| `forward` | Walk forward |
| `backward` | Walk backward |
| `turn_left` | Turn left |
| `turn_right` | Turn right |
| `trot` | Trot (faster walk) |
| `stretch` | Stretch body forward |
| `push_up` | Push-up exercise |
| `doze_off` | Doze off (nodding sleep motion) |
| `half_sit` | Half-sit position |
| `nod_lethargy` | Nod lethargically (drowsy head bobbing) |
| `shake_head` | Shake head side to side |
| `tilting_head_left` | Tilt head to the left |
| `tilting_head_right` | Tilt head to the right |
| `tilting_head` | Alternate tilting head left and right |
| `head_bark` | Head bark motion (look up) |
| `head_up_down` | Move head up and down |
| `wag_tail` | Wag tail motion |

## Prerequisites

- A **Raspberry Pi** with a **PiDog** robot kit attached
- The [`pidog`](https://github.com/sunfounder/pidog) library installed on the Pi
- Python 3.12+

## Installation

```bash
# Clone this repository
git clone https://github.com/yourusername/pidogmcp.git
cd pidogmcp

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## How to Run

### As an MCP Server (stdio transport)

```bash
python -m pidogmcp.server
```

Or using the project entry point:

```bash
pip install -e .
pidogmcp
```

### Connecting from an MCP Client

Configure your MCP client (e.g., Claude Desktop, Cursor, or a custom client) to connect to the server:

```json
{
  "mcpServers": {
    "pidogmcp": {
      "command": "python",
      "args": ["-m", "pidogmcp.server"],
      "cwd": "/path/to/pidogmcp"
    }
  }
}
```

## Usage Examples

### Execute an action
```
do_action(action_name="sit", step_count=1, speed=50, pitch_comp=0)
```

### Move legs directly
```
direct_legs_move(
  angles=[30, 60, -30, -60, 80, -45, -80, 45],
  speed=50
)
```

### Read battery voltage
```
get_battery_voltage()
```

### Play a sound
```
play_sound(name="pant", volume=100)
```

### Set RGB LED color
```
set_rgb_color(color="green", mode="breath", bps=1.0)
```

## Project Structure

```
pidogmcp/
├── pyproject.toml          # Project metadata & dependencies
├── README.md               # This file
└── pidogmcp/
    ├── __init__.py         # Package init
    └── server.py           # MCP server implementation
```

## Dependencies

- [`mcp`](https://pypi.org/project/mcp/) — Model Context Protocol SDK
- [`pidog`](https://github.com/sunfounder/pidog) — Sunfounder PiDog robot library

## Notes

- The PiDog library requires **root privileges** (`sudo`) for sound playback.
- Some features (IMU, ultrasonic, RGB) depend on the physical hardware being connected.
- Actions that involve movement will block until the robot completes the action.
- Always call `stop_robot` or `reset_robot` after use to safely shut down threads.

## License

This project is provided as-is for use with the Sunfounder PiDog robot.
