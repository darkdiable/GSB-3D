# 3D Solar System Simulation

A 3D solar system simulation built with Python and VPython, featuring the Sun and eight planets with realistic proportional scaling, orbital mechanics, and interactive camera controls.

## Features

- **Sun & Eight Planets**: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune
- **Proportional Scaling**: Planets sized relative to each other (visual scale)
- **Orbital Mechanics**: Each planet orbits at different speeds based on real planetary velocities
- **Planetary Rotation**: All planets spin on their axes
- **Orbit Lines**: Visual representation of each planet's orbital path
- **Name Labels**: Labels for each celestial body
- **Lighting Effects**: Sun as a light source with realistic shading
- **Interactive Camera**: Rotate, zoom, and pan controls
- **Starfield Background**: 200 stars for cosmic ambiance
- **Saturn's Rings**: Special ring system for Saturn

## Installation

```bash
cd solarSystem
pip install -r requirements.txt
```

## Usage

```bash
python solar_system.py
```

The simulation will open in your default web browser.

## Controls

- **Rotate View**: Right-click and drag
- **Zoom**: Scroll wheel or two-finger pinch
- **Pan**: Ctrl + right-click and drag (or middle mouse button)

## Planet Data

| Planet   | Relative Size | Orbit Radius | Orbit Speed (km/s) |
|----------|---------------|--------------|--------------------|
| Mercury  | 0.5           | 10           | 4.74               |
| Venus    | 0.9           | 14           | 3.50               |
| Earth    | 1.0           | 18           | 2.98               |
| Mars     | 0.6           | 23           | 2.41               |
| Jupiter  | 2.8           | 32           | 1.31               |
| Saturn   | 2.4           | 40           | 0.97               |
| Uranus   | 1.8           | 48           | 0.68               |
| Neptune  | 1.7           | 55           | 0.54               |

*Note: Sizes and distances are scaled for visual appeal, not astronomically accurate proportions.*
