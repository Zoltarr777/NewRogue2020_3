from __future__ import annotations
from typing import Iterator, Tuple, List, TYPE_CHECKING
import random
from game_map import GameMap
import tile_types
import tcod
import numpy as np

if TYPE_CHECKING:
	from entity import Entity

class RectangularRoom:
	def __init__(self, x: int, y: int, width: int, height: int):
		self.x1 = x
		self.y1 = y
		self.x2 = x + width
		self.y2 = y + height

	@property
	def center(self) -> Tuple[int, int]:
		center_x = int((self.x1 + self.x2) / 2)
		center_y = int((self.y1 + self.y2) / 2)

		return center_x, center_y

	@property
	def inner(self) -> Tuple[slice, slice]:
		#Return the inner area of this room as a 2D array index

		return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

	def intersects(self, other: RectangularRoom) ->bool:
		#Returns true if this room overlaps with another
		return (
			self.x1 <= other.x2
			and self.x2 >= other.x1
			and self.y1 <= other.y2
			and self.y2 >= other.y1
		)


def tunnel_between(
	start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
	#Return L-shaped tunnel between these points
	x1, y1 = start
	x2, y2 = end
	if random.random() < 0.5: #50% chance
		#move horizontally then vertically
		corner_x, corner_y = x2, y1
	else:
		#move vertically, then horizontally
		corner_x, corner_y = x1, y2

	#generate coordinates for the tunnel
	for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
		yield x, y
	for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
		yield x, y


def generate_dungeon(
	max_rooms: int,
	room_min_size: int,
	room_max_size: int,
	map_width: int,
	map_height: int,
	player: Entity,
	npc: Entity
) -> GameMap:

	#Fill map area with floor tiles
	dungeon = GameMap(map_width, map_height)

	rooms: List[RectangularRoom] = []

	for r in range(max_rooms):
		#randomize room sizes within bounds
		room_width = random.randint(room_min_size, room_max_size)
		room_height = random.randint(room_min_size, room_max_size)

		#randomize room coordinates within bounds
		x = random.randint(0, dungeon.width - room_width - 1)
		y = random.randint(0, dungeon.height - room_height - 1)

		#carve out room at location
		new_room = RectangularRoom(x, y, room_width, room_height)

		#if room intersects with another room, skip this one
		if any(new_room.intersects(other_room) for other_room in rooms):
			continue

		#set room tiles to floor
		dungeon.tiles[new_room.inner] = tile_types.floor

		center_of_last_room_x, center_of_last_room_y = new_room.center

		#set player spawn point
		if len(rooms) == 0:
			player.x, player.y = new_room.center
		else:
			for x, y in tunnel_between(rooms[-1].center, new_room.center):
				dungeon.tiles[x, y] = tile_types.floor

		#add rooms to list
		rooms.append(new_room)

	npc.x, npc.y = center_of_last_room_x, center_of_last_room_y

	return dungeon


def generate_cave(matrix):

	WALL = 0
	FLOOR = 1
	
	for i in range(matrix.shape[0]):
		for j in range(matrix.shape[1]):
			char = "#" if matrix[i][j] == WALL else " "
			print(char, end='')

		print()


def initialize_cave(map_width: int, map_height: int, player: Entity, npc: Entity):

	# Map area (height, width)
	shape = (map_height, map_width)

	WALL = 0
	FLOOR = 1

	# Wall fill probability
	fill_prob = 0.4

	new_map = np.ones(shape)

	for i in range(shape[0]):
		for j in range(shape[1]):
			choice = random.uniform(0, 1)
			new_map[i][j] = WALL if choice < fill_prob else FLOOR


	generations = 6

	for generation in range(generations):
		for i in range(shape[0]):
			for j in range(shape[1]):
				submap = new_map[max(i - 1, 0):min(i + 2, new_map.shape[0]), max(j - 1, 0):min(j + 2, new_map.shape[1])]
				wallcount_1away = len(np.where(submap.flatten() == WALL)[0])
				submap = new_map[max(i - 2, 0):min(i + 3, new_map.shape[0]), max(j - 2, 0):min(j + 3, new_map.shape[1])]
				wallcount_2away = len(np.where(submap.flatten() == WALL)[0])

				if generation < 5:
					if wallcount_1away >= 5 or wallcount_2away <= 7:
						new_map[i][j] = WALL
					else:
						new_map[i][j] = FLOOR
				else:
					if wallcount_1away >= 5:
						new_map[i][j] = WALL
					else:
						new_map[i][j] = FLOOR

				if i == 0 or j == 0 or i == shape[0] - 1 or j == shape[1] - 1:
					new_map[i][j] = WALL

	return new_map


































