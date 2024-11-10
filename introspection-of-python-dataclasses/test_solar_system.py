
from typing import Dict, List
import unittest
import solar_system
from solar_system import Planet, SolarSystem, get_dataclasses, get_type_description, get_field_default
from dataclasses import fields

class TestSolarSystem(unittest.TestCase):

    def test_planet_initialization(self):
        planet = Planet(name="Earth", mass=5.972e24)
        self.assertEqual(planet.name, "Earth")
        self.assertEqual(planet.mass, 5.972e24)
        self.assertFalse(planet.is_dwarf_planet)
        self.assertEqual(planet.solar_system, None)

    def test_solar_system_initialization(self):
        solar_system = SolarSystem(name="Solar System")
        self.assertEqual(solar_system.name, "Solar System")
        self.assertEqual(solar_system.planets, [])

    def test_add_planet(self):
        solar_system = SolarSystem(name="Solar System")
        planet = Planet(name="Mars", mass=6.39e23)
        solar_system.add_planet(planet)
        self.assertIn(planet, solar_system.planets)
        self.assertEqual(planet.solar_system, solar_system)

    def test_get_dataclasses(self):
        dataclasses = get_dataclasses(solar_system)
        self.assertIn(Planet, dataclasses)
        self.assertIn(SolarSystem, dataclasses)

    def test_get_type_description(self):
        self.assertEqual(get_type_description(None), "None")
        self.assertEqual(get_type_description("Something"), "str")
        self.assertEqual(get_type_description(str), "str")
        self.assertEqual(get_type_description(Planet), "Planet dataclass")
        self.assertEqual(get_type_description(List[Planet]), "List of Planet dataclass")
        self.assertEqual(get_type_description(Dict[str, Planet]), "Dict of str -> Planet dataclass")

    def test_get_field_default(self):
        planet_fields = fields(Planet)
        self.assertEqual(get_field_default(planet_fields[0]), "Required")  # name
        self.assertEqual(get_field_default(planet_fields[1]), "Defaults to 0.0")  # mass
        self.assertEqual(get_field_default(planet_fields[2]), "Defaults to None")  # solar_system
        self.assertEqual(get_field_default(planet_fields[3]), "Defaults to False")  # is_dwarf_planet
        solar_system_fields = fields(SolarSystem)
        self.assertEqual(get_field_default(solar_system_fields[1]), "Defaults to empty list") # planets

if __name__ == '__main__':
    unittest.main()

    