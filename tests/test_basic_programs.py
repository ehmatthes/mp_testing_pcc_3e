import subprocess, sys
from pathlib import Path
from shlex import split

import pytest

import utils


basic_programs = [
    # Chapter 1
    ("chapter_01/hello_world.py", "Hello Python world!"),

    # Chapter 2
    ("chapter_02/apostrophe.py", "One of Python's strengths is its diverse community."),
    ("chapter_02/comment.py", "Hello Python people!"),
    ("chapter_02/full_name.py", "ada lovelace"),
    ("chapter_02/full_name_2.py", "Hello, Ada Lovelace!"),
    ("chapter_02/full_name_3.py", "Hello, Ada Lovelace!"),
    ("chapter_02/hello_world.py", "Hello Python world!"),
    ("chapter_02/hello_world_variables.py", "Hello Python world!"),
    ("chapter_02/hello_world_variables_2.py", "Hello Python world!\nHello Python Crash Course world!"),
    ("chapter_02/name.py", "Ada Lovelace"),
    ("chapter_02/name_2.py", "ADA LOVELACE\nada lovelace"),

    # Chapter 3
    ("chapter_03/bicycles.py", "My first bicycle was a Trek."),
    ("chapter_03/cars.py", "['bmw', 'audi', 'toyota', 'subaru']\n['subaru', 'toyota', 'audi', 'bmw']"),
    ("chapter_03/motorcycles.py", "['honda', 'yamaha', 'suzuki', 'ducati']\n['honda', 'yamaha', 'suzuki']\n\nA Ducati is too expensive for me."),

    # Chapter 4
    ("chapter_04/dimensions.py", "Original dimensions:\n200\n50\n\nModified dimensions:\n400\n100"),
    ("chapter_04/even_numbers.py", "[2, 4, 6, 8, 10]"),
    ("chapter_04/first_numbers.py", "[1, 2, 3, 4, 5]"),
    ("chapter_04/foods.py", "My favorite foods are:\n['pizza', 'falafel', 'carrot cake', 'cannoli']\n\nMy friend\'s favorite foods are:\n['pizza', 'falafel', 'carrot cake', 'ice cream']"),
    ("chapter_04/magicians.py", "Alice, that was a great trick!\nI can't wait to see your next trick, Alice.\n\nDavid, that was a great trick!\nI can't wait to see your next trick, David.\n\nCarolina, that was a great trick!\nI can't wait to see your next trick, Carolina.\n\nThank you, everyone. That was a great magic show!"),
    ("chapter_04/players.py", "Here are the first three players on my team:\nCharles\nMartina\nMichael"),
    ("chapter_04/square_numbers.py", "[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]"),
    ("chapter_04/squares.py", "[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]"),
    
    # Chapter 5
    ("chapter_05/amusement_park.py", "Your admission cost is $25."),
    ("chapter_05/banned_users.py", "Marie, you can post a response if you wish."),
    ("chapter_05/cars.py", "Audi\nBMW\nSubaru\nToyota"),
    ("chapter_05/magic_number.py", "That is not the correct answer. Please try again!"),
    ("chapter_05/toppings.py", "Adding mushrooms.\nSorry, we don't have french fries.\nAdding extra cheese.\n\nFinished making your pizza!"),
    ("chapter_05/voting.py", "Sorry, you are too young to vote.\nPlease register to vote as soon as you turn 18!"),
    
    # Chapter 6
    ("chapter_06/alien.py", "{'color': 'green', 'points': 5}\n{'color': 'green'}"),
    ("chapter_06/alien_no_points.py", "No point value assigned."),
    ("chapter_06/aliens.py", "{'color': 'yellow', 'points': 10, 'speed': 'medium'}\n{'color': 'yellow', 'points': 10, 'speed': 'medium'}\n{'color': 'yellow', 'points': 10, 'speed': 'medium'}\n{'color': 'green', 'points': 5, 'speed': 'slow'}\n{'color': 'green', 'points': 5, 'speed': 'slow'}\n...\nTotal number of aliens: 30"),
    ("chapter_06/favorite_languages.py", "Jen's favorite languages are:\n\tPython\n\tRust\n\nSarah's favorite languages are:\n\tC\n\nEdward's favorite languages are:\n\tRust\n\tGo\n\nPhil's favorite languages are:\n\tPython\n\tHaskell"),
    ("chapter_06/many_users.py", "Username: aeinstein\n\tFull name: Albert Einstein\n\tLocation: Princeton\n\nUsername: mcurie\n\tFull name: Marie Curie\n\tLocation: Paris"),
    ("chapter_06/pizza.py", "You ordered a thick-crust pizza with the following toppings:\n\tmushrooms\n\textra cheese"),
    ("chapter_06/user.py", "Key: username\nValue: efermi\n\nKey: first\nValue: enrico\n\nKey: last\nValue: fermi"),
    
    # Chapter 7
    ("chapter_07/confirmed_users.py", "Verifying user: Candace\nVerifying user: Brian\nVerifying user: Alice\n\nThe following users have been confirmed:\nCandace\nBrian\nAlice"),
    ("chapter_07/counting.py", "1\n3\n5\n7\n9"),
    ("chapter_07/pets.py", "['dog', 'cat', 'dog', 'goldfish', 'cat', 'rabbit', 'cat']\n['dog', 'dog', 'goldfish', 'rabbit']"),
    
    # Chapter 8
    ("chapter_08/formatted_name.py", "Jimi Hendrix\nJohn Lee Hooker"),
    ("chapter_08/person.py", "{'first': 'jimi', 'last': 'hendrix', 'age': 27}"),
    ("chapter_08/pets.py", "I have a dog.\nMy dog's name is Willie."),
    ("chapter_08/pizza.py", "Making a 16-inch pizza with the following toppings:\n- pepperoni\n\nMaking a 12-inch pizza with the following toppings:\n- mushrooms\n- green peppers\n- extra cheese"),
    ("chapter_08/printing_models.py", "Printing model: dodecahedron\nPrinting model: robot pendant\nPrinting model: phone case\n\nThe following models have been printed:\ndodecahedron\nrobot pendant\nphone case"),
    ("chapter_08/user_profile.py", "{'location': 'princeton', 'field': 'physics', 'first_name': 'albert', 'last_name': 'einstein'}"),

    # Chapter 9
    ("chapter_09/car.py", "2019 Subaru Outback\nThis car has 23500 miles on it.\nThis car has 23600 miles on it."),
    ("chapter_09/dog.py", "My dog's name is Willie.\nMy dog is 6 years old.\nWillie is now sitting.\n\nYour dog's name is Lucy.\nYour dog is 3 years old.\nLucy is now sitting."),
    ("chapter_09/electric_car.py", "2024 Nissan Leaf\nThis car has a 40-kWh battery.\nThis car can go about 150 miles on a full charge."),
]

@pytest.mark.parametrize(
    "file_path, expected_output", basic_programs)
def test_basic_program(python_cmd, file_path, expected_output):
    """Test a program that only prints output."""
    root_dir = Path(__file__).parents[1]
    path = root_dir / file_path

    # Run the command, and make assertions.
    cmd = f"{python_cmd} {path}"
    output = utils.run_command(cmd)

    assert output == expected_output