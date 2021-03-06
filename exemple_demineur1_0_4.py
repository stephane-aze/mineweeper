import random
import arcade
from sklearn.neural_network import MLPRegressor
import numpy as np

# Import image tools used to create our tiles
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

DEFAULT_LEARNING_RATE = 1e-3
DEFAULT_DISCOUNT_FACTOR = 0.1
NOISE_INIT = 0.5
NOISE_DECAY = 0.9

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
SCREEN_HEIGHT = (HEIGHT + MARGIN) * ROW_COUNT + MARGIN+60
SCREEN_TITLE = "Démineur"
#VALUES_MINES_NEAR = [1,2,3,4]
MINES = """
11111
11111
11211
15251
11211
"""
# Colors
BACKGROUND_COLOR = 119, 110, 101
BACKGROUND_COLOR_CASE = 238, 228, 218
BACKGROUND_COLOR_TABLE = 192,192,192

TEXT_COLOR_DARK = 119, 110, 101
TEXT_COLOR_LIGHT = 245, 149, 99
TEXT_COLOR_1 = 178,34,34
TEXT_COLOR_2= 30,144,255
TEXT_COLOR_3= 0,128,0
TEXT_COLOR_4= 75,0,130
SQUARE_COLORS = TEXT_COLOR_LIGHT,   \
                TEXT_COLOR_1, \
                TEXT_COLOR_2,   \
                TEXT_COLOR_3,   \
                TEXT_COLOR_4    \

# Sizes
BOARD_SIZE = 4
SQUARE_SIZE = 40
TEXT_SIZE = 20
#REWARD
REWARD_GOAL = 60
REWARD_DEFAULT = 10
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
                if self.lines[row][col] == '5':
                    self.bombs.append((row, col))
        self.grid[(1,0)] = 1

    def mine(self, state, action,  case_courante):
        if action == 1:
            if self.states[(case_courante[0],case_courante[1])] == '5':
                reward = REWARD_IMPOSSIBLE
            else:
                self.grid[(case_courante[0],case_courante[1])] = 1
                reward = REWARD_DEFAULT
        else:
            reward = 0    
        return reward, case_courante
    def initial_grid(self):
        for row in range(self.height):
            for col in range(len(self.lines[row])):
                self.grid[(row, col)] = 0
        self.grid[(1,0)] = 1

class Agent:
    def __init__(self, environment):
        self.environment = environment
        self.policy = Policy(environment)
        self.reset()
    
    def reset(self):
        x, y = 2,1
        self.case_courante = []
        self.case_courante.append(x)
        self.case_courante.append(y)
        self.case_precedente = self.case_courante
        self.grid_a = self.grid_en_place(x,y)
        self.board_a = self.board_en_place(x,y)
        self.state = self.board_to_state(self.board_a,self.grid_a)
        self.previous_state = self.state
        self.score = 0
        self.timer=0
        self.environment.initial_grid()

    def board_to_state(self, board_a, grid_a):
        vector = []
        compteur = 0 
        while compteur < 8 :
            if grid_a[compteur] == 1:
                if board_a[compteur] == '1':
                    vector.append(0)
                elif board_a[compteur] == '2':
                    vector.append(1)
                else:
                    vector.append(2)
            else:
                vector.append(8)
            compteur = compteur + 1
        return vector

    def grid_en_place(self, x, y): 
        grid_a = []
        self.ajout_liste(x-1,y-1,"grille",grid_a)
        self.ajout_liste(x-1,y,"grille",grid_a)
        self.ajout_liste(x-1,y+1,"grille",grid_a)
        self.ajout_liste(x,y-1,"grille",grid_a)
        self.ajout_liste(x-1,y+1,"grille",grid_a)
        self.ajout_liste(x+1,y-1,"grille",grid_a)
        self.ajout_liste(x+1,y,"grille",grid_a)
        self.ajout_liste(x+1,y+1,"grille",grid_a)
        return grid_a

    def board_en_place(self, x , y):
        board_a = []
        self.ajout_liste(x-1,y-1,"board",board_a)
        self.ajout_liste(x-1,y,"board",board_a)
        self.ajout_liste(x-1,y+1,"board",board_a)
        self.ajout_liste(x,y-1,"board",board_a)
        self.ajout_liste(x-1,y+1,"board",board_a)
        self.ajout_liste(x+1,y-1,"board",board_a)
        self.ajout_liste(x+1,y,"board",board_a)
        self.ajout_liste(x+1,y+1,"board",board_a)
        return board_a

    def ajout_liste(self, x, y, la_liste, tableau):
        if la_liste=="grille":
            if x<5 and x>0 and y<5 and y>0:
                tableau.append(self.environment.grid[(x,y)])
            else:
                tableau.append(-1)
        else:
            if x<5 and x>0 and y<5 and y>0:
                tableau.append(self.environment.states[(x,y)])
            else:
                tableau.append(-1)

    def best_action(self):
        return self.policy.best_action(self.state)

    def do(self, action):
        self.previous_state = self.board_to_state(self.board_a,self.grid_a)
        self.reward, self.case_precedente = self.environment.mine(self.state, action,  self.case_courante)
        x, y = self.choix_case()
        self.case_courante[0] = x
        self.case_courante[1] = y
        self.grid_a = self.grid_en_place(x,y)
        self.board_a = self.board_en_place(x,y)
        self.state = self.board_to_state(self.board_a,self.grid_a)
        self.score += self.reward
        self.last_action = action

    def choix_case(self):
        x = random.randint(0,4)
        y = random.randint(0,4)
        while(self.environment.grid[(x,y)]==1):
            x = random.randint(0,4)
            y = random.randint(0,4)
            
        return x , y
        

    def update_policy(self):
        self.policy.update(self.previous_state, self.state, self.last_action, self.reward)
    
class Policy:
    def __init__(self, environment,
                 learning_rate = DEFAULT_LEARNING_RATE,
                 discount_factor = DEFAULT_DISCOUNT_FACTOR):
       
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.mlp = MLPRegressor(hidden_layer_sizes = (20, ),
                                max_iter = 1,
                                activation = 'tanh', 
                                solver = 'sgd',
                                learning_rate_init = self.learning_rate,
                                warm_start = True)
        self.actions = [0,1] # Crée une liste de size*size actions
        self.noise = NOISE_INIT
        
        #On initialise le ANN avec 8 entrées, 2 sorties
        self.mlp.fit([[0,0,0,0,0,0,0,0]], [[0, 0]])
    
    """
    def __repr__(self):
        res = ''
        for state in self.table:
            res += f'{state}\t{self.table[state]}\n'
        return res
    """

    def best_action(self, state):
        self.proba_state = self.mlp.predict([state]) #Le RN fournit un vecteur de probabilité
        self.noise *= NOISE_DECAY
        self.proba_state += np.random.rand(len(self.proba_state)) * self.noise
        action = self.actions[np.argmax(self.proba_state)] #On choisit l'action la plus probable
        return action

    def update(self, previous_state, state, last_action, reward):
        #Q(st, at) = Q(st, at) + learning_rate * (reward + discount_factor * max(Q(state)) - Q(st, at))
        #Mettre le réseau de neurone à jour, au lieu de la table
        maxQ = np.amax(self.proba_state)
        self.proba_state[last_action] = reward + self.discount_factor * maxQ
        inputs = [state]
        outputs = [self.proba_state]
        #print(inputs, outputs)
        self.mlp.fit(inputs, outputs)

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
        img = Image.new('RGB', (SQUARE_SIZE, SQUARE_SIZE), color=BACKGROUND_COLOR_CASE)
        #
        d = ImageDraw.Draw(img)
        font = ImageFont.truetype(FONT, TEXT_SIZE)
        text = f"{self.value}"
        text_w, text_h = d.textsize(text, font)
        x = WIDTH - WIDTH / 2 - text_w / 2
        y = HEIGHT - HEIGHT / 2 - text_h / 2

        if self.value == '5' :
            color = TEXT_COLOR_DARK
            d.text((x, y), text, fill=color, font=font)
            self.texture = arcade.Texture(f"{self.value}", img)
            #self.texture = arcade.load_texture(":resources:images/tiles/bomb.png",width=WIDTH,height=HEIGHT)


        else:
            color = SQUARE_COLORS[int(self.value)]
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
        if (self.agent.case_courante[0],self.agent.case_courante[1]) not in self.agent.environment.bombs:
            action = self.agent.best_action()
            self.agent.do(action)
            self.update_grid(self.agent.case_precedente)
            self.agent.timer+=delta_time
        else:
            self.agent.environment.mine(self.agent.state,self.agent.last_action,self.agent.case_courante)

    def update_grid(self,case_up):
        if self.agent.environment.grid[(case_up[0],case_up[1])] == 0:
            self.agent.environment.grid[(case_up[0],case_up[1])] = 1
            self.grid_sprites[case_up[0]][case_up[1]].face_up()
    
    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()
        output = f"Score: {self.agent.score:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 20, arcade.color.BLACK, 16)
        output = f"Temps: {self.agent.timer:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 50, arcade.color.BLACK, 16)

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