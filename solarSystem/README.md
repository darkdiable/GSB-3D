# 3D Solar System Simulation

A 3D solar system simulation built with Python and Panda3D, featuring the Sun and eight planets with realistic proportional scaling, orbital mechanics, and interactive camera controls.

## Features

- **Sun & Eight Planets**: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune
- **3D Models**: All planets rendered as 3D spheres with materials
- **Orbital Mechanics**: Each planet orbits at different speeds based on real planetary velocities
- **Planetary Rotation**: All planets spin on their axes
- **Orbit Lines**: Visual circular orbit paths for each planet
- **Name Labels**: Billboard labels for each celestial body (always face camera)
- **Lighting Effects**: Sun as point light source with realistic shading and ambient light
- **Interactive Camera**: Full keyboard controls for rotating and zooming
- **Starfield Background**: 500 stars for cosmic ambiance
- **Saturn's Rings**: Special ring system for Saturn
- **Sun Glow Effect**: Emissive sun with glow effect

## Installation

```bash
cd solarSystem
pip install -r requirements.txt
```

## Usage

### Panda3D Version (Recommended)

```bash
python solar_system_panda3d.py
```

A window will open with the 3D simulation.

### VPython Version

```bash
python solar_system.py
```

The simulation will open in your default web browser.

## Controls (Panda3D Version)

- **Arrow Keys**: Rotate camera around the solar system
- **W / S**: Zoom in / out
- **+ / -**: Speed up / slow down simulation
- **ESC**: Exit

## Planet Data

| Planet   | Radius | Orbit Radius | Orbit Speed (km/s) |
|----------|--------|--------------|--------------------|
| Mercury  | 1.2    | 12           | 4.74               |
| Venus    | 1.8    | 17           | 3.50               |
| Earth    | 2.0    | 23           | 2.98               |
| Mars     | 1.5    | 29           | 2.41               |
| Jupiter  | 4.0    | 38           | 1.31               |
| Saturn   | 3.5    | 47           | 0.97               |
| Uranus   | 2.8    | 56           | 0.68               |
| Neptune  | 2.7    | 65           | 0.54               |

*Note: Sizes and distances are scaled for visual appeal, not astronomically accurate proportions.*
