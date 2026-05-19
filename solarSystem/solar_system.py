from vpython import *
import math

scene.title = "3D Solar System Simulation"
scene.width = 1200
scene.height = 800
scene.background = color.black
scene.autoscale = False
scene.range = 70

sun_light = local_light(pos=vector(0, 0, 0), color=color.white)
distant_light(direction=vector(1, 0, 0), color=color.gray(0.3))

sun = sphere(
    pos=vector(0, 0, 0),
    radius=4,
    color=color.yellow,
    emissive=True,
    shininess=1
)
sun_label = label(
    pos=sun.pos,
    text="Sun",
    yoffset=20,
    color=color.yellow,
    height=16,
    box=False,
    line=False
)

planets_data = [
    {
        "name": "Mercury",
        "radius": 1.2,
        "orbit_radius": 10,
        "orbit_speed": 4.74,
        "rotation_speed": 0.03,
        "color": color.gray(0.7),
        "texture": textures.rough
    },
    {
        "name": "Venus",
        "radius": 1.6,
        "orbit_radius": 14,
        "orbit_speed": 3.50,
        "rotation_speed": 0.005,
        "color": color.orange,
        "texture": textures.rough
    },
    {
        "name": "Earth",
        "radius": 1.8,
        "orbit_radius": 18,
        "orbit_speed": 2.98,
        "rotation_speed": 0.1,
        "color": color.blue,
        "texture": textures.earth
    },
    {
        "name": "Mars",
        "radius": 1.4,
        "orbit_radius": 23,
        "orbit_speed": 2.41,
        "rotation_speed": 0.09,
        "color": color.red,
        "texture": textures.rough
    },
    {
        "name": "Jupiter",
        "radius": 3.5,
        "orbit_radius": 32,
        "orbit_speed": 1.31,
        "rotation_speed": 0.2,
        "color": color.orange,
        "texture": textures.wood
    },
    {
        "name": "Saturn",
        "radius": 3.0,
        "orbit_radius": 40,
        "orbit_speed": 0.97,
        "rotation_speed": 0.18,
        "color": color.yellow.orange(),
        "texture": textures.rough
    },
    {
        "name": "Uranus",
        "radius": 2.2,
        "orbit_radius": 48,
        "orbit_speed": 0.68,
        "rotation_speed": 0.15,
        "color": color.cyan,
        "texture": textures.rough
    },
    {
        "name": "Neptune",
        "radius": 2.1,
        "orbit_radius": 55,
        "orbit_speed": 0.54,
        "rotation_speed": 0.16,
        "color": color.blue,
        "texture": textures.rough
    }
]

planets = []
orbits = []
labels_list = []

for data in planets_data:
    orbit = ring(
        pos=vector(0, 0, 0),
        radius=data["orbit_radius"],
        thickness=0.1,
        color=color.gray(0.4),
        axis=vector(0, 1, 0)
    )
    orbits.append(orbit)

    planet = sphere(
        pos=vector(data["orbit_radius"], 0, 0),
        radius=data["radius"],
        color=data["color"],
        texture=data["texture"],
        shininess=0.5
    )
    planets.append(planet)

    lbl = label(
        pos=planet.pos,
        text=data["name"],
        yoffset=15,
        color=color.white,
        height=12,
        box=False,
        line=False
    )
    labels_list.append(lbl)

saturn_ring = ring(
    pos=planets[5].pos,
    radius=4.5,
    thickness=0.2,
    color=color.gray(0.8),
    axis=vector(0.5, 1, 0)
)

stars = []
for i in range(200):
    theta = 2 * math.pi * random()
    phi = math.acos(2 * random() - 1)
    r = 80 + random() * 40
    x = r * math.sin(phi) * math.cos(theta)
    y = r * math.sin(phi) * math.sin(theta)
    z = r * math.cos(phi)
    star = sphere(
        pos=vector(x, y, z),
        radius=0.1,
        color=color.white,
        emissive=True
    )
    stars.append(star)

angle = [0] * len(planets_data)

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
