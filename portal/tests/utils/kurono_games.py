from typing import Tuple

from common.models import Class
from aimmo.models import Game, Worksheet


def generate_name():
    name = "Game %d" % generate_name.next_id

    generate_name.next_id += 1

    return name


generate_name.next_id = 1


def create_kurono_game_directly(
    klass: Class, worksheet: Worksheet
) -> Tuple[Game, str]:
    """Generate a Kurono game with the details given.

    Args:
        klass (Class): The instance of the class.
        worksheet (Worksheet): The instance of the worksheet.

    Returns:
        (game: Game, name: str): A tuple with the game model instance and its name.
    """
    name = generate_name()

    game = Game.objects.create(name=name, game_class=klass, worksheet=worksheet)

    return game, name
