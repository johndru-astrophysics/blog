# Overview
This article contains:

* A brief introduction to Python dataclasses and introspection
* An example of a dataclass model to store data
* Details on how to programmatically inspect our example model

Prerequisites:
* Basic Python knowledge including defining classes

You can find the source code used in this article on GitHub:

https://github.com/johndru-astrophysics/blog/blob/main/introspection-of-python-dataclasses/solar_system.py

# Introduction

## What are dataclasses?

Python dataclasses are a simple way to create Python classes to hold structured data. For example, to create a class to store data related to a planet’s mass:

```python
from dataclasses import dataclass

@dataclass
class Planet:
    name: str
    mass: int
    is_dwarf_planet: bool = False
```

Then, to create instances of the `Planet` class, you can provide keyword arguments as follows:

```python
saturn = Planet(name='Saturn', mass=568.34e24)
pluto = Planet(name='Pluto', mass=1.303e22, is_dwarf_planet=True)
```

To access the instance field values, use dot notation, such as:

```python
print(saturn.mass) # returns 568.34e24
```

For more details see the dataclass package documentation: [https://docs.python.org/3/library/dataclasses.html](https://docs.python.org/3/library/dataclasses.html)

## What is introspection?

Introspection, also called reflection or metaprogramming, is a way to programmatically inspect the structure of a class.

### Why is this useful?

Applications of introspection include:

* Converting to data structures in other programming languages, such as C/C++ for performance-critical code and Dart for building GUIs with Flutter.
* Serialization and deserialization, for example when reading and writing JSON.
* Automatic documentation generation, including class diagrams.
* Form generation.
* Syntax checkers, highlights, and linters.
* ORM (Object-Relational Mapping) when working with databases such as MySQL and PostGres.

For more information see the following page: https://en.wikipedia.org/wiki/Reflective_programming

# Solar System Example

We are going to create a model of a solar system containing planets.

Let's start with the `Planet` class, with some fields for storing data about the planet's mass and orbit:

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
* A reference to a "SolarSystem" object. The class name is enclosed in double quotes because we create this class later in the model.

Next, we define the `SolarSystem` class:

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

The `Planet` class name does not need double quotes because it is already defined above this class in the model.

The `planet` field is initialized with a `default_factory` of `list`. You must do this for all lists and dictionaries in a dataclass.

The `add_planet` method is used to add a planet to this solar system, we will see later how this works.

# Introspection methods

Now we are going to write some Python code to inspect the dataclasses in our model.


## Step 1: Finding dataclasses in a module

There are 2 functions we can use to find all members (classes, functions, etc.) of a module, then determine if the member is a dataclass:

1. `inspect.getmembers` - returns all members of the specified module
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

`field.name` returns the name of the field and `field.type` returns an object representing the type of the field.

The code above should output the following:

```plain
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

Each field type can include various properties such as:

* Is the field a list or dict?
* Does the field reference another dataclass?
* Is the field optional?
* Does the field have a default value?

So, how do we post-process the field's type?

Each field has a type, accessed with `field.type`. We can inspect that type to determine what to do. We are going to create a function that given a type, returns a description of that type we can use later:

```python
def get_type_description(field_type: Type) -> str:
    ...
```

1. Is type None? Then return "None".
1. Is type an instance of a string? Then return "str".
1. Is type a reference to a dataclass? Return `"<dataclass-name> dataclass"`
1. Is type a list? Recursively call `get_type_description` to return the list types then return `"list of <sub-type-description>"`.
1. Is type a dict? Recursively call `get_type_description` and the key type and the value type to return the dict types then return `"dict of <key-type-description> -> <value-type-description>"`.
1. For everything else, just return `field_type.__name__`. For example, int would return "int" and float would return "float" etc.

Here is the code to perform each of those checks:

```python
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
```

For example:

```python
get_type_description(str)                # returns "str"
get_type_description(Planet)             # returns "Planet dataclass"
get_type_description(List[Planet])       # returns "List of Planet dataclass"
get_type_description(Dict[str, Planet])  # returns "Dict of str -> Planet dataclass"
get_type_description(List[List[Planet]]) # returns "List of List of Planet dataclass"
```

## Step 4: Determining the default value of a field, and if it is required

Each field can have a default value, if it has no default value, then the field is required.

We are going to create a function to return the default value, like this:

```python
def get_field_default(field: Field) -> str:
  ...
```

We can determine the default value of a field using the following steps:

1. Does the field have `field.default_factory`? If so, the field will default to empty.
2. Does the field have `field.default`? If so, the field default value is `field.default`
3. Otherwise, the field does not have a default value, so it is required.

Here is the code to return a field's default value:

```python
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
```


# Summary

We created a simple model using Python dataclasses, to model a solar system and its planets.

Then we created 3 functions to:

1. Find all dataclasses in a Python module
1. Return a dataclass field type as a string
1. Return a dataclass field default value

## Putting it all together

We can now use all the code we created to print a summary of a module's dataclasses and their fields:

```python
for dataclass in get_dataclasses(solar_system):
    print(dataclass.__name__)

    for field in fields(dataclass):
        type_name = get_type_description(field.type)
        default_value = get_field_default(field)
        print(f"  {field.name} ({type_name}) : {default_value}")
    print()
```

You should see the following output:

```plain
Planet
  name (str) : Required
  mass (float) : Defaults to 0.0
  solar_system (str) : Defaults to None
  is_dwarf_planet (bool) : Defaults to False
  semi_major_axis (float) : Defaults to 0.0
  eccentricity (float) : Defaults to 0.0
  inclination (float) : Defaults to 0.0
  orbital_period (float) : Defaults to 0.0

SolarSystem
  name (str) : Required
  planets (List of Planet dataclass) : Defaults to empty list

```
