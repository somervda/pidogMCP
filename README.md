# PiDog MCP Server

A **FastMCP** (Model Context Protocol) server that wraps the [Sunfounder PiDog](https://github.com/sunfounder/pidog) robot API, exposing robot control operations as MCP tools over HTTP.

## What It Does

This project runs a remote MCP service on port **8080** that lets any MCP-compatible client (such as an AI assistant or chat interface) control a PiDog robot by calling tools. Available capabilities include:

| Category | Tools |
|---|---|
| **Actions** | `do_action` — Execute 21 predefined actions (stand, sit, walk, trot, bark, etc.) |
| **Movement** | `legs_move`, `head_move`, `head_move_raw`, `tail_move` — Direct servo control |
| **Pose** | `set_pose`, `set_rpy` — Adjust body position and orientation |
| **Sensors** | `read_distance`, `get_battery_voltage` — Read ultrasonic sensor and battery |
| **Audio** | `speak` — Play sound files |
| **LED** | `rgb_set_mode` — Control RGB LED strip |
| **Control** | `body_stop`, `wait_all_done`, `list_actions` — Stop movement, wait, list actions |

## Prerequisites

- **Python 3.12+**
- **PiDog hardware** connected to a Raspberry Pi (this server talks to physical hardware)
- The `pidog` Python package installed on the device

> **Note:** The PiDog library requires hardware-specific dependencies (`robot_hat`, etc.) that only work on Raspberry Pi with the PiDog HAT attached. The MCP server itself can be developed anywhere, but it must run on the Pi to control the robot.

## Installation

```bash
# Clone or navigate to the project
cd pidogMCP

# Create virtual environment and install dependencies
pip install -e .

# Or with uv:
uv sync
```

## Running the Server

```bash
# Default: listens on all interfaces, port 8080
python -m pidogmcp.server

# Or via the installed entry point
pidogmcp
```

### Configuration

| Environment Variable | Default      | Description |
|---------------------|--------------|-------------|
| `PIDOGMCP_HOST`     | `0.0.0.0`    | Bind address |
| `PIDOGMCP_PORT`     | `8080`       | Port number |

```bash
# Example: run on a custom port
PIDOGMCP_PORT=9000 python -m pidogmcp.server
```

### Connect to the Server

Once running, connect your MCP client to:

```
http://localhost:8080/mcp
```

## Available Tools

### `do_action`
Execute a predefined robot action. Valid actions:

- **Legs:** `stand`, `sit`, `lie`, `lie_with_hands_out`, `forward`, `backward`, `turn_left`, `turn_right`, `trot`, `stretch`, `push_up`, `doze_off`, `half_sit`
- **Head:** `nod_lethargy`, `shake_head`, `tilting_head_left`, `tilting_head_right`, `tilting_head`, `head_bark`, `head_up_down`
- **Tail:** `wag_tail`

### `legs_move`
Move legs to specified angles (8 servo angles).

### `head_move` / `head_move_raw`
Move head by yaw/roll/pitch angles or raw servo values.

### `tail_move`
Move the tail servo.

### `set_pose` / `set_rpy`
Adjust body position (x, y, z) and orientation (roll, pitch, yaw).

### `speak`
Play a sound file by name.

### `read_distance`
Read the ultrasonic distance sensor (cm).

### `get_battery_voltage`
Read the current battery voltage.

### `body_stop`
Stop all movement immediately.

### `wait_all_done`
Block until all queued movements complete.

### `list_actions`
List all valid action names.

### `rgb_set_mode`
Set the RGB LED strip mode and color.

## Project Structure

```
pidogMCP/
├── pidogmcp/
│   └── server.py      # FastMCP server with all tool definitions
├── pyproject.toml      # Project metadata and dependencies
└── README.md
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Safety Notes

- The PiDog is a physical robot — actions produce real movement.
- Always test with the robot on a soft surface.
- Use `body_stop` to halt all movement immediately if needed.
- The server initializes the robot hardware on first tool call and cleans up on shutdown.
