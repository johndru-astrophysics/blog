# Overview
This article contains:

* A brief introduction to Python dataclasses and introspection
* An example of a dataclass model to store data
* Details on how to programatically inspect our example model

Prerequisists:
* Basic python knowledge including defining classes

# Introduction

## What are dataclasses?

Python dataclasses are a simple way to create Python classes to hold structured data. For example, to create a class to store data related to a planet’s mass:

```python
from dataclasses import dataclass

@dataclass
class Planet:
    name: str
    mass_kg: int
    is_dwarf_planet: bool = False
```

Then, to create instances of the `Planet` class, you can provide keyword arguments as folows:

```python
saturn = Planet(name='Saturn', mass_kg=568.34e24)
pluto = Planet(name='Pluto', mass_kg=1.303e22, is_dwarf_planet=True)
```

To access the instance field values, use dot notation, such as:

```python
print(saturn.mass_kg)
```

For more details see the dataclass package documentation: [https://docs.python.org/3/library/dataclasses.html](https://docs.python.org/3/library/dataclasses.html)

## What is introspection?

Introspection, also called reflection or metaprograming, is a way to programatically inspect the structure of a class.

### Why is this useful?

Applications of introspection include:

* Converting to data structures in other programming languages, such as C/C++ for performance critical code and Dart for building GUIs with Flutter.
* Serialization and deserialization, for example when reading and writing JSON.
* Automatic documentation generation, including class diagrams.
* Form generation.    
* Syntax checkers, highlights and linters.
* ORM (Object-Relational Mapping) when working with databases such as MySQL and PostGres.

For more information see the following page: https://en.wikipedia.org/wiki/Reflective_programming

# Solar System Example

We are going to create a model of a solar system containing planets.

Let's start with the `Planet` class, with a some fields for storing data about the planets mass and orbit:

```python
from dataclasses import dataclass, field
from typing import List


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
    mass_kg: float = 0.0
    solar_system: "SolarSystem" = None
    is_dwarf_planet: bool = False
    semi_major_axis: float = 0.0
    eccentricity: float = 0.0
    inclination: float = 0.0
    orbital_period: float = 0.0
```

The `Planet` class contains:
* A description of the class, including any units used. This is important to help developers using this model and for generating documentation.
* A reference to a "SolarSystem" object. The class name is enclosed in double-quotes because we create this class later in the model.

Next we define the `SolarSystem` class:

```python
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
```

A `SolarSystem` class contains:
* The name of the solar system, which is a required field.
* A list of planets.

The `Planet` class name does not need double quotes because it is already define above this class in the model.

The `planet` field is initalized with a `default_factory` of `list`. You must do this for all lists and dictonaries in a dataclass.

The `add_planet` method is used to add a planet to this solar system, we will see later how this works.

# Introspection methods

Now we are going to write some Python code to inspect the dataclasses in our model.


## Step 1: Finding dataclasses in a module

There are 2 functions we can use to find all members (classes, functions etc) of a module, then determine if the member is a dataclass:

1. `inspect.getmembers` - returns all members if the specified module
2. `is_dataclass` - returns True if the specified member is a dataclass

We can write the following function to return all dataclasses in a specific module:

```python
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
```

Example usage:

```python
dataclasses_in_module: List[Type] = get_dataclasses(solar_system)
for dataclass in dataclasses_in_module:
    print(dataclass.__name__)
```

## Step 2: Finding fields of a dataclass

We will use the `fields` function to find all fields of a specific dataclass:

```python
for dataclass in get_dataclasses(solar_system):
    print(dataclass.__name__)

    for field in fields(dataclass):
        print(f"  {field.name}: {field.type}")
```

`field.name` returns the name of the field and `field.type` return an object representing the type of the field.

The code above should output the following:

```shell
Planet
  name: <class 'str'>
  mass: <class 'float'>
  solar_system: SolarSystem
  is_dwarf_planet: <class 'bool'>
  semi_major_axis: <class 'float'>
  eccentricity: <class 'float'>
  inclination: <class 'float'>
  orbital_period: <class 'float'>
SolarSystem
  name: <class 'str'>
  planets: typing.List[solar_system.Planet]
```

## Step 3: Determining the properties of the field

Each field type can included various properties such as:

* Is the field a list or dict?
* Does the field reference another dataclass?
* Is the field optional?
* Does the field have a default value?

So, how to we post-process the fields type? Let's start with figuring out basic (primtive) types, such as str, int, float etc.




# Generating a dataclass diagram

Show how to generate a dataclass diagram using dot syntax. Or maybe latex or something.