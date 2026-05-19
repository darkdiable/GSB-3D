from vpython import *
import math

scene.title = "3D Solar System Simulation"
scene.width = 1400
scene.height = 900
scene.background = color.black
scene.autoscale = False
scene.range = 80
scene.forward = vector(0, -0.3, -1)

sun_light = local_light(pos=vector(0, 0, 0), color=color.white)
distant_light(direction=vector(1, 0.5, 1), color=color.gray(0.4))

sun = sphere(
    pos=vector(0, 0, 0),
    radius=5,
    color=color.yellow,
    emissive=True,
    shininess=1
)
sun_label = label(
    pos=sun.pos,
    text="Sun",
    yoffset=30,
    color=color.yellow,
    height=18,
    box=False,
    line=False
)

planets_data = [
    {
        "name": "Mercury",
        "radius": 3.0,
        "orbit_radius": 12,
        "orbit_speed": 4.74,
        "rotation_speed": 0.03,
        "color": color.gray(0.7),
        "start_angle": 0.0
    },
    {
        "name": "Venus",
        "radius": 3.8,
        "orbit_radius": 18,
        "orbit_speed": 3.50,
        "rotation_speed": 0.005,
        "color": color.orange,
        "start_angle": 0.8
    },
    {
        "name": "Earth",
        "radius": 4.0,
        "orbit_radius": 25,
        "orbit_speed": 2.98,
        "rotation_speed": 0.1,
        "color": color.blue,
        "start_angle": 1.6
    },
    {
        "name": "Mars",
        "radius": 3.4,
        "orbit_radius": 32,
        "orbit_speed": 2.41,
        "rotation_speed": 0.09,
        "color": color.red,
        "start_angle": 2.4
    },
    {
        "name": "Jupiter",
        "radius": 6.0,
        "orbit_radius": 42,
        "orbit_speed": 1.31,
        "rotation_speed": 0.2,
        "color": color.orange,
        "start_angle": 3.2
    },
    {
        "name": "Saturn",
        "radius": 5.2,
        "orbit_radius": 52,
        "orbit_speed": 0.97,
        "rotation_speed": 0.18,
        "color": color.yellow.orange(),
        "start_angle": 4.0
    },
    {
        "name": "Uranus",
        "radius": 4.4,
        "orbit_radius": 62,
        "orbit_speed": 0.68,
        "rotation_speed": 0.15,
        "color": color.cyan,
        "start_angle": 4.8
    },
    {
        "name": "Neptune",
        "radius": 4.2,
        "orbit_radius": 72,
        "orbit_speed": 0.54,
        "rotation_speed": 0.16,
        "color": color.blue,
        "start_angle": 5.6
    }
]

planets = []
orbits = []
labels_list = []

for data in planets_data:
    orbit = ring(
        pos=vector(0, 0, 0),
        radius=data["orbit_radius"],
        thickness=0.15,
        color=color.gray(0.5),
        axis=vector(0, 1, 0)
    )
    orbits.append(orbit)

    start_x = data["orbit_radius"] * math.cos(data["start_angle"])
    start_z = data["orbit_radius"] * math.sin(data["start_angle"])
    
    planet = sphere(
        pos=vector(start_x, 0, start_z),
        radius=data["radius"],
        color=data["color"],
        shininess=0.5,
        visible=True
    )
    planets.append(planet)

    lbl = label(
        pos=planet.pos,
        text=data["name"],
        yoffset=35,
        color=color.white,
        height=16,
        box=False,
        line=False
    )
    labels_list.append(lbl)

saturn_ring = ring(
    pos=planets[5].pos,
    radius=7.5,
    thickness=0.3,
    color=color.gray(0.8),
    axis=vector(0.5, 1, 0)
)

stars = []
for i in range(300):
    theta = 2 * math.pi * random()
    phi = math.acos(2 * random() - 1)
    r = 100 + random() * 60
    x = r * math.sin(phi) * math.cos(theta)
    y = r * math.sin(phi) * math.sin(theta)
    z = r * math.cos(phi)
    star = sphere(
        pos=vector(x, y, z),
        radius=0.15,
        color=color.white,
        emissive=True
    )
    stars.append(star)

angle = [data["start_angle"] for data in planets_data]

while True:
    rate(60)

    for i, planet in enumerate(planets):
        data = planets_data[i]
        angle[i] += data["orbit_speed"] * 0.002
        x = data["orbit_radius"] * math.cos(angle[i])
        z = data["orbit_radius"] * math.sin(angle[i])
        planet.pos = vector(x, 0, z)
        planet.rotate(angle=data["rotation_speed"] * 0.1, axis=vector(0, 1, 0))
        labels_list[i].pos = planet.pos

    saturn_ring.pos = planets[5].pos
    saturn_ring.rotate(angle=0.01, axis=vector(0, 1, 0))

    sun.rotate(angle=0.002, axis=vector(0, 1, 0))
