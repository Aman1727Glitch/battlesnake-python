import bottle
import json
import math

width = 0
height = 0
snake_name = 'nake'
jer_snake = 'Swift Snake'
taunt_count = 0
head = []

@bottle.get('/')
def index():
  return """
    <a href="https://github.com/sendwithus/battlesnake-python">
      battlesnake-python
    </a>
    """


@bottle.post('/start')
def start():
  global width, height
  data = bottle.request.json
  width = data['width']
  height = data['height']

  return json.dumps({
    "color": "#FF0000",
    "secondary_color": "#00FF00",
    "head_url": "http://placecage.com/c/100/100",
    "name": "Cage Snake",
    "taunt": "OH GOD NOT THE BEES",
    "head_type": "fang",
    "tail_type": "pixel"
    }
  )


@bottle.post('/move')
def move():
  global taunt_count, head

  data = bottle.request.json

  print data
  print data['snakes']
  print '=================='

  snake_butts = []
  hungry = False

  # get data for my snake, target snake
  # TODO: update for first snake in array that's not me ?
  for snake in data['snakes']:
    if snake['name'] == snake_name:
      head = snake['coords'][0]
      my_data = snake
      my_length = len(snake['coords'])
      if len(snake['coords']) == 3 or (data['turn'] - snake['last_eaten'] > 60):
        hungry = True

  final_countdown = False

  # find the snake_butts
  if len(data['snakes']) > 2:
    for snake in data['snakes']:
      # if snake isn't me
      if snake['name'] != snake_name:
        snake_butt, snake_head = find_snake_parts(snake)
        # don't append if snake is adjacent and growing
        if square_adjacent(snake_butt, head) and snake_butt == snake['coords'][len(snake['coords'])-2]:
          print 'WATCH OUT IT\'S GROWING!!!'
        else:
          print 'we\'ve got a new butt'
          snake_butts.append(snake_butt)
    else:
      final_countdown = True


  food = data['food']

  safe_squares = find_safe_square(head, data)
  print 'safe_squares', safe_squares


  # if hungry or snake i'm following is growing, find food.
  if hungry or snake_butts == []:
    print 'im hungry'
    closest_food = find_closest(food, head)
    taunt_count = 0
    
    # another snake could be going for the same food
    if not adjacent_square_safe(closest_food, data):
      if closest_food in safe_squares:
        safe_squares.remove(closest_food)

    best_move = find_closest(safe_squares, closest_food)
  # otherwise follow a snake
  else:
    closest_butt = find_closest(snake_butts, head)
    print 'snake_butts', snake_butts
    print 'closest', closest_butt

    if square_adjacent(head, snake_butt) and snake_butt in snake_butts:
      safe_squares.append(snake_butt)

    best_move = find_closest(safe_squares, snake_butt)

    if taunt_count < 8:
      taunt_count += 1
    else:
      taunt_count = 1


  print 'best_move', best_move

  # convert best move from coordinates into a string
  best_move = convert_coord_to_move(best_move, head)
  print 'best move', best_move

  taunt = taunt_gen()

  return json.dumps({
    'move': best_move,
    'taunt': taunt
  })


def square_adjacent(head, snake_butt):
  adj = False

  x = head[0]
  y = head[1]

  left = [x-1, y]
  right = [x+1, y]
  up = [x, y-1]
  down = [x, y+1]

  if snake_butt == left or snake_butt == right or snake_butt == up or snake_butt == down:
    adj = True

  return adj

def find_closest(choices, coord):
  temp_closest = choices[0]
  temp_min_dist = pow(width,2)
  for c in choices:
    a = abs(c[1] - coord[1])
    b = abs(c[0] - coord[0])
    distance = math.sqrt( pow(a, 2) + pow(b, 2))
    if distance < temp_min_dist:
      temp_min_dist = distance
      temp_closest = c
  return temp_closest

def adjacent_square_safe(point, data):
  x = point[0]
  y = point[1]

  left = [x-1, y]
  right = [x+1, y]
  up = [x, y-1]
  down = [x, y+1]

  directions = [left, right, up, down]

  safe_sq = True

  for direction in directions:
    if direction[0] < (width) and direction[0] >=0:
      if direction[1] < (height) and direction[1] >= 0:
        if not square_empty(direction, data):
          safe_sq = False
  return safe_sq

def find_safe_square(head, data):

  global width, height
  x = head[0]
  y = head[1]

  left = [x-1, y]
  right = [x+1, y]
  up = [x, y-1]
  down = [x, y+1]

  directions = [left, right, up, down]

  safe_sq = []

  for direction in directions:
    if direction[0] < (width) and direction[0] >= 0:
      if direction[1] < (height) and direction[1] >= 0:
        if square_empty(direction, data):
          print 'square empty!!'
          safe_sq.append(direction)
  return safe_sq

def find_snake_parts(snake):
  snake_butt = snake['coords'][len(snake['coords'])-1]
  snake_head = snake['coords'][0]
  return snake_butt, snake_head


def taunt_gen():
  if taunt_count == 1:
    return 'MY ANACONDA'
  elif taunt_count == 2:
    return 'DON\'T'
  elif taunt_count == 3:
    return 'WANT'
  elif taunt_count == 4:
    return 'NONE'
  elif taunt_count == 5:
    return 'UNLESS YOU'
  elif taunt_count == 6:
    return 'GOT'
  elif taunt_count == 7:
    return 'BUNS'
  elif taunt_count == 8:
    return 'HUN'
  else:
    return 'My anaconda don\'t'

def convert_coord_to_move(best_move, head):
  x = head[0]
  y = head[1]

  left = [x-1, y]
  right = [x+1, y]
  up = [x, y-1]
  down = [x, y+1]

  if best_move == left:
    return 'left'
  elif best_move == right:
    return 'right'
  elif best_move == up:
    return 'up'
  elif best_move == down:
    return 'down'
  else:
    print 'you fucked up'

def square_empty(square, data):
  empty = True
  print 'square_empty'
  for snake in data['snakes']:
    print 'SNAKE IS'
    print square
    print snake
    if square in snake['coords']:

      empty = False 
      print 'Square empty'
      return empty
  
  return empty


@bottle.post('/end')
def end():
  data = bottle.request.json

  return json.dumps({})


# Expose WSGI app
application = bottle.default_app()
