import tcod

from engine import Engine
from entity import Entity
from input_handlers import EventHandler
from procgen import generate_dungeon, generate_cave, initialize_cave

def main() -> None:
	screen_width = 120
	screen_height = 70

	map_width = screen_width
	map_height = screen_height

	room_max_size = 10
	room_min_size = 6
	max_rooms = 100

	tileset = tcod.tileset.load_tilesheet("dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD)
	#tileset = tcod.tileset.load_tilesheet("terminal32x32.png", 16, 16, tcod.tileset.CHARMAP_CP437)

	event_handler = EventHandler()

	player = Entity(int(screen_width / 2), int(screen_height / 2), "@", (255, 255, 0))
	npc = Entity(int(screen_width / 2 - 12), int(screen_height / 2 - 5), "@", (255, 255, 255))
	entities = {npc, player}

	map_type = 2

	if map_type == 1:
		game_map = generate_dungeon(
			max_rooms=max_rooms,
			room_min_size=room_min_size,
			room_max_size=room_max_size,
			map_width=map_width,
			map_height=map_height,
			player=player,
			npc=npc
		)

	else:
		game_map = initialize_cave(
			map_width=map_width,
			map_height=map_height,
			player=player,
			npc=npc
		)

		generate_cave(game_map)

	engine = Engine(entities=entities, event_handler=event_handler, game_map=game_map, player=player)


	with tcod.context.new_terminal(
		screen_width,
		screen_height,
		tileset=tileset,
		title="New Roguelike 2020 Version 2",
		vsync=True,
	) as context:
		root_console = tcod.Console(screen_width, screen_height, order="F")
		while True:
			
			engine.render(console=root_console, context=context)

			events = tcod.event.wait()

			engine.handle_events(events)


if __name__ == "__main__":
	main()


