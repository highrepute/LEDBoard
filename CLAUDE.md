# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

LEDBoard is a PyQt5 desktop application for managing a climbing wall with addressable LED holds. It runs on a Raspberry Pi and controls WS281x NeoPixel LEDs. Users can log in, browse climbing problems, and light up the corresponding holds on the physical board.

## Running the App

**On Raspberry Pi (production):**
```bash
# From the parent directory of LEDBoard/:
bash start-LEDBoard.sh
# This uses ~/my-venv if present (Pi 4), otherwise system python3 (Pi 3)
# Must run with sudo for GPIO/LED access
```

**Direct launch (from repo root):**
```bash
sudo python3 DiscoMain.py
```

**On Windows/dev (no LEDs):** Set `LINUX = 0` in `config.ini`, then run `python DiscoMain.py`.

There are no automated tests. Manual testing is the only verification method.

## Configuration

All runtime settings live in `config.ini`. Key settings:
- `LINUX` — `1` for Raspberry Pi (enables LED hardware + `rpi_ws281x`), `0` for Windows dev
- `BOARDNAME` — path to the active `.brd` file
- `IMAGEPATH` — path to the board photo used as background
- `TOTALLEDCOUNT` — number of LEDs on the board
- Paths section: absolute paths to `users.csv`, `logs.csv`, `problems.csv`, `projects.csv`

`const.py` wraps all config access. Call `const.initConfigVariables()` once at startup (already done in `DiscoMain.py`).

## Architecture

**Entry point:** `DiscoMain.py` — a single large PyQt5 `QMainWindow` subclass (`MyApp`) that handles all UI logic. The UI layout is defined in `DiscoBoard.ui` (Qt Designer file).

**Data layer** (all use CSV files, no database):
- `problemFuncs.py` (`problemClass`) — read/write climbing problems (`problems.csv`)
- `usersFuncs.py` (`userClass`) — users and passwords (`users.csv`)
- `logFuncs.py` (`logClass`) — session logs (`logs.csv`)
- `projectFuncs.py` (`projectClass`) — user project lists (`projects.csv`)

**Board data:**
- `boardMaker.py` (`boardMaker`) — reads/writes `.brd` files (CSV format). Row 0 = image path, row 1 = mirror table (Python list literal), remaining rows = hold data.
- `mirror.py` (`mirror`) — maps hold IDs to their mirrored counterparts using the board's mirror table.

**UI helpers:**
- `dragButton.py` (`DragButton`) — QPushButton subclass that supports drag-to-reposition (used for holds on the board overlay).
- `qrangeslider.py` (`QRangeSlider`) — third-party dual-handle range slider widget (used for grade filtering).

**Hardware:** LED control uses `rpi_ws281x` (Pi 4) or `neopixel` (Pi 3 legacy), imported conditionally. Requires `sudo` to access GPIO.

## `.brd` File Format

Custom CSV format for board layouts:
- Line 0: image path
- Line 1: mirror table as a Python list of `[holdA, holdB]` pairs
- Lines 2+: hold data rows

## Data Files

`users.csv`, `problems.csv`, `logs.csv`, `projects.csv` — all CSV, first row is header. Paths are configured in `config.ini` under `[PATHS]`. Column indices for problem fields are constants in `const.py` (e.g., `PROBNAMECOL=0`, `GRADECOL=1`, `HOLDSINDEX=22`).
