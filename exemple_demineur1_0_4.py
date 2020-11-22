import random
import arcade

# Import image tools used to create our tiles
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Face down image
FACE_DOWN_IMAGE = ":resources:images/tiles/brickBrown.png"

# Set how many rows and columns we will have
ROW_COUNT = 5
COLUMN_COUNT = 5

# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 50
HEIGHT = 50

# This sets the margin between each cell
# and on the edges of the screen.
MARGIN = 5

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = (WIDTH + MARGIN) * COLUMN_COUNT + MARGIN
SCREEN_HEIGHT = (HEIGHT + MARGIN) * ROW_COUNT + MARGIN
SCREEN_TITLE = "Démineur"
#VALUES_MINES_NEAR = [1,2,3,4]
MINES = """
01211
1B3B1
23B32
1B3B1
11211
"""
# Colors
BACKGROUND_COLOR = 119, 110, 101
EMPTY_CELL = 205, 193, 180
TEXT_COLOR_DARK = 119, 110, 101
TEXT_COLOR_LIGHT = 245, 149, 99
SQUARE_COLORS = (205, 193, 180), \
                (238, 228, 218), \
                (237, 224, 200), \
                (242, 177, 121), \
                (245, 149, 99), \
                (246, 124, 95), \
                (246, 94, 59), \
                (237, 207, 114), \
                (237, 204, 97), \
                (237, 200, 80), \
                (237, 197, 63), \
                (237, 194, 46), \
                (62, 57, 51)

# Sizes
BOARD_SIZE = 4
SQUARE_SIZE = 40
TEXT_SIZE = 20
#REWARD
REWARD_GOAL = 60
REWARD_DEFAULT = -1
REWARD_STUCK = -6
REWARD_IMPOSSIBLE = -60


# Font
FONT = "arial.ttf"
class Environment:
    def __init__(self, text):
        self.states = {}
        self.lines = text.strip().split('\n')

        self.height = len(self.lines)
        self.width = len(self.lines[0]) 
        self.grid = {}  
        self.bombs =[]
        for row in range(self.height):
            
            for col in range(len(self.lines[row])):
                self.states[(row, col)] = self.lines[row][col]
                self.grid[(row, col)] = 0
                if self.lines[row][col] == 'B':
                    self.bombs.append((row, col))
                elif self.lines[row][col] == '0':
                    self.starting_point = (row, col)
    def mine(self, state, action):


        if self.states[action] == 'B':
            reward = REWARD_IMPOSSIBLE
        else:
            self.grid[action] = 1
            reward = REWARD_DEFAULT
            
        return action, reward

class Agent:
    def __init__(self, environment):
        self.environment = environment
        self.reset()
    def reset(self):
        self.state = self.environment.starting_point
        self.previous_state = self.state
        self.score = 0

    
    def do(self, action):
        self.previous_state = self.state
        self.state, self.reward = self.environment.mine(self.state, action)
        self.score += self.reward
        self.last_action = action

    """def update_policy(self):
        self.policy.update(agent.previous_state, agent.state, self.last_action, self.reward)
        """
class Case(arcade.Sprite):
    """ Case sprite """

    def __init__(self, value, scale=1):
        """ Case constructor """

        self.value = value

        # Image to use for the sprite when face up
        self.image_file_name = ""
        self.is_face_up = False
        super().__init__(FACE_DOWN_IMAGE, scale)

    def face_down(self):
        """ Turn case face-down """
        self.texture = arcade.load_texture(FACE_DOWN_IMAGE,width=WIDTH,height=HEIGHT)
        self.is_face_up = False

    def face_up(self):
        """ Turn case face-up """
        img = Image.new('RGB', (SQUARE_SIZE, SQUARE_SIZE), color=SQUARE_COLORS[1])
        #
        d = ImageDraw.Draw(img)
        font = ImageFont.truetype(FONT, TEXT_SIZE)
        text = f"{self.value}"
        text_w, text_h = d.textsize(text, font)
        x = WIDTH - WIDTH / 2 - text_w / 2
        y = HEIGHT - HEIGHT / 2 - text_h / 2

        if self.value == 'B' :
            color = TEXT_COLOR_DARK
            d.text((x, y), text, fill=color, font=font)
            self.texture = arcade.Texture(f"{self.value}", img)
            #self.texture = arcade.load_texture(":resources:images/tiles/bomb.png")
        else:
            color = TEXT_COLOR_LIGHT
            d.text((x, y), text, fill=color, font=font)
            self.texture = arcade.Texture(f"{self.value}", img)
        
        

        self.is_face_up = True

    @property
    def is_face_down(self):
        """ Is this case face down? """
        return not self.is_face_up

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, agent):
        """
        Set up the application.
        """

        super().__init__(SCREEN_WIDTH,
                        SCREEN_HEIGHT,
                        SCREEN_TITLE)
        arcade.set_background_color(arcade.color.ALMOND)
        # Create a 2 dimensional array. A two dimensional
        # array is simply a list of lists.
        self.grid_sprite_list = None
        self.grid_sprites = None
        self.agent = agent
        self.grid_res= None


    def setup(self):
        """
        Set the game up for play. Call this to reset the game.
        :return:
        """
        self.grid_sprite_list = arcade.SpriteList()
        self.grid_sprites = []
        self.grid_res= {}

        for row in range(ROW_COUNT):
            # Add an empty array that will hold each cell
            # in this row
            self.grid_sprites.append([])
            for col in range(COLUMN_COUNT):
                x = col * (WIDTH + MARGIN) + (WIDTH / 2 + MARGIN)
                y = row * (HEIGHT + MARGIN) + (HEIGHT / 2 + MARGIN)
                #sprite2 = arcade.SpriteSolidColor(WIDTH, HEIGHT, arcade.color.WHITE)
                
                sprite = Case(self.agent.environment.lines[row][col])
                sprite.center_x = x
                sprite.center_y = y
                sprite.height=HEIGHT
                sprite.width=WIDTH
                """
                sprite.position=x,y"""
                self.grid_sprite_list.append(sprite)
                self.grid_sprites[row].append(sprite)
                self.grid_res[(row, col)] = self.agent.environment.lines[row][col]
    def on_update(self, delta_time):
        if self.agent.state not in self.agent.environment.bombs:
            x, y = random.randrange(5), random.randrange(5)
            action = (x, y)
            self.agent.do(action)
            #self.agent.update_policy()
            self.update_grid(x, y)
    def update_grid(self,row, col):
        case=self.grid_sprites[row][col]
        if case.is_face_down:
                case.face_up()
    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        self.grid_sprite_list.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            self.agent.reset()
            self.setup()
def main():
    environment = Environment(MINES)
    agent = Agent(environment)
    my_game=MyGame(agent)
    my_game.setup()
    arcade.run()


if __name__ == "__main__":
    main()