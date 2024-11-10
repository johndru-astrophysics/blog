from dataclasses import MISSING, Field, dataclass, field, fields, is_dataclass
from typing import Any, Dict, List, Type, get_args, get_origin
from types import ModuleType
import inspect
import solar_system

@dataclass
class Planet:
    """
    A planet in the solar system.

    Attributes:
        name (str): The name of the planet.
        mass (int): The mass of the planet in kilograms.
        solar_system (SolarSystem): The solar system the planet belongs to.
        is_dwarf_planet (bool): Indicates if the planet is a dwarf planet. Defaults to False.
        semi_major_axis (float): The semi-major axis of the planet's orbit in astronomical units (AU).
        eccentricity (float): The eccentricity of the planet's orbit.
        inclination (float): The inclination of the planet's orbit in degrees.
        orbital_period (float): The orbital period of the planet in Earth years.
    """
    name: str
    mass: float = 0.0
    solar_system: "SolarSystem" = None
    is_dwarf_planet: bool = False
    semi_major_axis: float = 0.0
    eccentricity: float = 0.0
    inclination: float = 0.0
    orbital_period: float = 0.0

@dataclass
class SolarSystem:
    """
    A solar system with planets.
    
    Args:
        name (str): The name of the solar system.
        planets (List[Planet]): A list of planets in the solar system.
    """
    name: str
    planets: List[Planet] = field(default_factory=list)
    
    def add_planet(self, planet: Planet):
        """
        Adds a planet to the solar system and updates the planet's solar_system field.

        Args:
            planet (Planet): The planet to add.
        """
        planet.solar_system = self
        self.planets.append(planet)

# How to list all dataclasses in a module
def get_dataclasses(module: ModuleType) -> List[Type]:
    """
    Retrieves all dataclass types defined in the given module.

    Args:
        module (ModuleType): The module to inspect for dataclasses.

    Returns:
        List[Type]: A list of dataclass types found in the module.
    """
    return [cls for name, cls in inspect.getmembers(module) if is_dataclass(cls)]

def get_type_description(field_type: Type) -> str:
    """
    Retrieves the description of a type.

    Args:
        field_type (Type): The type to retrieve the description of.

    Returns:
        str: The name of the type.
    """
    if field_type is None:
        return "None"
    elif is_dataclass(field_type):
        return f"{field_type.__name__} dataclass"
    elif isinstance(field_type, str):
        return "str"
    elif get_origin(field_type) is list:
        sub_type = get_args(field_type)[0]
        return f"List of {get_type_description(sub_type)}"
    elif get_origin(field_type) is dict:
        key_type, value_type = get_args(field_type)
        return f"Dict of {get_type_description(key_type)} -> {get_type_description(value_type)}"
    else:
        return field_type.__name__

def get_field_default(field: Field) -> str:
    """
    Retrieves the default value of a field.

    Args:
        field (Field): The field to retrieve the default value of.

    Returns:
        Any: The default value of the field.
    """
    if field.default_factory != MISSING:
        return f"Defaults to empty {get_type_description(field.default_factory)}"
    elif field.default != MISSING:
        return f"Defaults to {field.default}"
    else:
        return "Required"
    
if __name__ == "__main__":

    for dataclass in get_dataclasses(solar_system):
        print(dataclass.__name__)
    
        for field in fields(dataclass):
            type_name = get_type_description(field.type)
            default_value = get_field_default(field)
            print(f"  {field.name} ({type_name}) : {default_value}")
        print()


