from aimmo.models import Game, Worksheet
from common.models import Class


def generate_name():
    name = "Game %d" % generate_name.next_id

    generate_name.next_id += 1

    return name


generate_name.next_id = 1


def create_aimmo_game_directly(klass: Class, worksheet: Worksheet) -> Game:
    """Generate an aimmo game with the details given.

    Args:
        klass (Class): The instance of the class.
        worksheet (Worksheet): The instance of the worksheet.

    Returns:
        game: Game: The game model instance.
    """
    name = generate_name()

    game = Game.objects.create(name=name, game_class=klass, worksheet=worksheet)

    return game
