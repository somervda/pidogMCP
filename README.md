# PiDog MCP Server

Remote Model Context Protocol (MCP) server that wraps the SunFounder PiDog robot API, exposing convenient tools to trigger robot actions, play sounds, and read sensors over HTTP.

## What It Does
- Hosts a remote MCP server (FastMCP) on port 8080.
- Wraps the PiDog Python API (`pidog.Pidog`) with tools:
  - `do_action(action_name, step_count, speed, pitch_comp)` — run built‑in actions.
  - `stop_and_lie(speed)` — stop and return to rest posture.
  - `speak(name, volume)` — play a built‑in sound.
  - `read_distance()` — ultrasonic distance (cm).
  - `get_battery_voltage()` — current battery voltage (V).
  - `shutdown()` — gracefully release hardware resources.

`do_action` supports these action names:
`stand, sit, lie, lie_with_hands_out, forward, backward, turn_left, turn_right, trot, stretch, push_up, doze_off, nod_lethargy, shake_head, tilting_head_left, tilting_head_right, tilting_head, head_bark, wag_tail, head_up_down, half_sit`.

## Requirements
- Run on the PiDog device (Raspberry Pi) with the official SunFounder stack installed.
- Python 3.12+
- The `pidog` package and hardware dependencies must be installed on the device (typically via SunFounder setup scripts).

## Install
Using [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv sync
```

Or with pip:

```bash
pip install -e .
```

Note: Ensure the PiDog Python library and dependencies are installed per SunFounder instructions.

## Run the Server (HTTP 8080)

```bash
# On the PiDog device
uv run python -m pidogmcp.server
# or
python -m pidogmcp.server
```

Environment overrides:

```bash
# Optional
set HOST=0.0.0.0  # default
set PORT=8080     # default
```

The MCP endpoint will be available at:

```
http://<device-ip>:8080/mcp
```

## Connect from a Client
- MCP Inspector:
  ```bash
  npx -y @modelcontextprotocol/inspector
  # In the UI, connect to: http://<device-ip>:8080/mcp
  ```
- Claude Code (example):
  ```bash
  claude mcp add --transport http pidog http://<device-ip>:8080/mcp
  ```

## Troubleshooting
- Import error for `pidog`: Run this server on the PiDog and ensure the SunFounder setup is complete.
- Permission or audio issues: Some PiDog functions require elevated permissions; follow SunFounder guidance (e.g., `sudo` for audio).
- Hardware not moving: Verify I2C and servo connections, and that the robot is powered.
