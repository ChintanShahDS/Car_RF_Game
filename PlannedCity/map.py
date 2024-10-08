# Self Driving Car

# Importing the libraries
import numpy as np
from random import random, randint
import matplotlib.pyplot as plt
import time

# Importing the Kivy packages
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line
from kivy.config import Config
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from PIL import Image as PILImage
from kivy.graphics.texture import Texture

# Importing the Dqn object from our AI in ai.py
from ai import Dqn

# Adding this line if we don't want the right click to put a red point
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '1279')
Config.set('graphics', 'height', '900')

# Introducing last_x and last_y, used to keep the last point in memory when we draw the sand on the map
last_x = 0
last_y = 0
n_points = 0
length = 0

# To bring in randomness
randomChoices = [True, False]

rng1 = np.random.default_rng()
rng2 = np.random.default_rng()
randomnessProbability = [0.3,0.7] # First part is for randomness and other is for the brains data

# Getting our AI, which we call "brain", and that contains our neural network that represents our Q-function
brain = Dqn(5,3,0.9)
action2rotation = [0,5,-5]
end2rotation = [10,-10,20,-20,30,-30]
last_reward = 0
scores = []
im = CoreImage("./map/PlannedCity_mask.png")

# textureMask = CoreImage(source="./kivytest/simplemask1.png")


# Initializing the map
first_update = True
def init():
    global sand
    global goal_x
    global goal_y
    global first_update
    global mapsize
    # print("longueur:", longueur, "largeur:", largeur)
    # sand = np.zeros((longueur,largeur))
    # print("sand shape:", sand.shape)
    img = PILImage.open("./map/PlannedCity_mask_upd.png").convert('L')
    sand = np.asarray(img)/255
    print("sand shape:", sand.shape)
    global mapwidth
    global mapheight
    mapwidth, mapheight = sand.shape
    print("After mapwidth:", mapwidth, "mapheight:", mapheight)
    mapsize = np.sqrt((mapwidth)**2 + (mapheight)**2)
    goal_x = 1055
    goal_y = 595
    first_update = False
    global swap
    swap = 0


# Initializing the last distance
last_distance = 0

# Creating the car class

class Car(Widget):
    
    angle = NumericProperty(0)
    rotation = NumericProperty(0)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    sensor1_x = NumericProperty(0)
    sensor1_y = NumericProperty(0)
    sensor1 = ReferenceListProperty(sensor1_x, sensor1_y)
    sensor2_x = NumericProperty(0)
    sensor2_y = NumericProperty(0)
    sensor2 = ReferenceListProperty(sensor2_x, sensor2_y)
    sensor3_x = NumericProperty(0)
    sensor3_y = NumericProperty(0)
    sensor3 = ReferenceListProperty(sensor3_x, sensor3_y)
    signal1 = NumericProperty(0)
    signal2 = NumericProperty(0)
    signal3 = NumericProperty(0)

    def move(self, rotation):
        last_pos = self.pos.copy()
        print("lastpos:", last_pos, "velocity:", self.velocity)
        self.pos = Vector(*self.velocity) + self.pos
        self.rotation = rotation
        if (self.velocity == [0,0]):
            print("At same place with velocity:", self.velocity, "pos:", self.pos, "lastpos:", last_pos)
            self.rotation = 90
        self.angle = self.angle + self.rotation
        if self.angle > 360 or self.angle < -360:
            self.angle = 0
        self.sensor1 = Vector(30, 0).rotate(self.angle) + self.pos
        self.sensor2 = Vector(30, 0).rotate((self.angle+30)%360) + self.pos
        self.sensor3 = Vector(30, 0).rotate((self.angle-30)%360) + self.pos
        self.signal1 = int(np.sum(sand[int(self.sensor1_x)-10:int(self.sensor1_x)+10, int(self.sensor1_y)-10:int(self.sensor1_y)+10]))/400.
        self.signal2 = int(np.sum(sand[int(self.sensor2_x)-10:int(self.sensor2_x)+10, int(self.sensor2_y)-10:int(self.sensor2_y)+10]))/400.
        self.signal3 = int(np.sum(sand[int(self.sensor3_x)-10:int(self.sensor3_x)+10, int(self.sensor3_y)-10:int(self.sensor3_y)+10]))/400.
        # Setting the signal to 3 in case it is to the end of the map - Earlier this was set to 10
        if self.sensor1_x>longueur-10 or self.sensor1_x<10 or self.sensor1_y>largeur-10 or self.sensor1_y<10:
            self.signal1 = 5.
        if self.sensor2_x>longueur-10 or self.sensor2_x<10 or self.sensor2_y>largeur-10 or self.sensor2_y<10:
            self.signal2 = 5.
        if self.sensor3_x>longueur-10 or self.sensor3_x<10 or self.sensor3_y>largeur-10 or self.sensor3_y<10:
            self.signal3 = 5.
        print(f"signal1: {self.signal1} signal2: {self.signal2} signal3: {self.signal3} pos: {self.pos}")
        

class Ball1(Widget):
    pass
class Ball2(Widget):
    pass
class Ball3(Widget):
    pass
class Flag(Widget):
    pass

# Creating the game class

class Game(Widget):

    car = ObjectProperty(None)
    ball1 = ObjectProperty(None)
    ball2 = ObjectProperty(None)
    ball3 = ObjectProperty(None)
    flag = ObjectProperty(None)

    def serve_car(self):
        self.car.center = self.center
        self.car.velocity = Vector(6, 0)
        # self.width = 1429
        # self.height = 660

    def update(self, dt):

        global brain
        global last_reward
        global scores
        global last_distance
        global goal_x
        global goal_y
        global longueur
        global largeur
        global swap
        
        # longueur = self.width
        # largeur = self.height
        # print("Update longueur:", longueur, "largeur:", largeur)
        if first_update:
            init()
        longueur = mapwidth
        largeur = mapheight
        print("Late longueur:", longueur, "largeur:", largeur)

        xx = goal_x - self.car.x
        yy = goal_y - self.car.y
        # print("velocity:", self.car.velocity, "xx:", xx, "yy:", yy, "Angle:")
        orientation = Vector(*self.car.velocity).angle((xx,yy))/180.
        # print("orientation:", orientation)
        last_signal = [self.car.signal1, self.car.signal2, self.car.signal3, self.car.angle/180.0, orientation]
        action = brain.update(last_reward, last_signal)

        randomChoice = rng1.choice(randomChoices, 1, p=randomnessProbability)
        if randomChoice:
            action = rng2.choice(len(action2rotation))
            print("Random action taken:", action)

        print("last_signal:", last_signal, "last_reward:", last_reward, "action:", action)
        scores.append(brain.score())
        # print("action:", action)
        rotation = action2rotation[action]
        # print("rotation:", rotation)
        self.car.move(rotation)
        distance = np.sqrt((self.car.x - goal_x)**2 + (self.car.y - goal_y)**2)
        self.ball1.pos = self.car.sensor1
        self.ball2.pos = self.car.sensor2
        self.ball3.pos = self.car.sensor3
        self.flag.pos = [goal_x-20, goal_y-20]

        distReward = 0.0
        locReward = 0.0
        dirReward = 0.0
        edgeReward = 0.0
        distWeight = 0.2
        locWeight = 0.4
        dirWeight = 0.4
        edgeWeight = 1.0

        # Location Reward - Directly based on signal1 from sensor1
        # Will be from +1 to -1 based on car signal which is from 0 to 1 where full sand is 1 and so subtraction
        locReward = 2.0 * (0.5 - self.car.signal1)
        # Distance Reward is based on how close the car is to the destination
        # Need to look at some log of the distance to properly handle it
        distReward = 1.0 - distance/mapsize
        if distance < last_distance:
            dirReward = 1.0
        else:
            dirReward = -1.0

        # Velocity calculations for the car
        # Though no loss required for the velocity directly since the location covers that part
        if sand[int(self.car.x),int(self.car.y)] > 0:
            self.car.velocity = Vector(0.5, 0).rotate(self.car.angle)
        else: # otherwise
            self.car.velocity = Vector(2, 0).rotate(self.car.angle)

        # if sand[int(self.car.x),int(self.car.y)] > 0:
        #     self.car.velocity = Vector(0.5, 0).rotate(self.car.angle)
        #     print(1, goal_x, goal_y, distance, int(self.car.x),int(self.car.y), im.read_pixel(int(self.car.x),int(self.car.y)))
            
        #     last_reward = -1
        #     if distance > last_distance:
        #         last_reward = last_reward-((last_distance - distance) / last_distance)

        # else: # otherwise
        #     self.car.velocity = Vector(2, 0).rotate(self.car.angle)
        #     last_reward = -0.1
        #     print(0, goal_x, goal_y, distance, int(self.car.x),int(self.car.y), im.read_pixel(int(self.car.x),int(self.car.y)))
        #     if distance < last_distance:
        #         last_reward = 1.0 - ((last_distance - distance) / last_distance)
        #         print("last_reward:", last_reward)
        #     # else:
        #     #     last_reward = last_reward +(-0.2)

        # Changed since the height and width seems different causing error
        # Introduced randomness in terms of angle change
        if self.car.x < 5:
            self.car.x = 5
            anglechg = rng2.choice(len(end2rotation))
            self.car.angle = self.car.angle + anglechg
            edgeReward = -1
        # if self.car.x > self.width - 5:
        #     self.car.x = self.width - 5
        #     last_reward = -1
        if self.car.x > mapwidth - 5:
            self.car.x = mapwidth - 5
            anglechg = rng2.choice(len(end2rotation))
            self.car.angle = self.car.angle + anglechg
            edgeReward = -1
        if self.car.y < 5:
            self.car.y = 5
            anglechg = rng2.choice(len(end2rotation))
            self.car.angle = self.car.angle + anglechg
            edgeReward = -1
        # if self.car.y > self.height - 5:
        #     self.car.y = self.height - 5
        #     last_reward = -1
        if self.car.y > mapheight - 5:
            self.car.y = mapheight - 5
            anglechg = rng2.choice(len(end2rotation))
            self.car.angle = self.car.angle + anglechg
            edgeReward = -1

        last_reward = locReward * locWeight + distReward * distWeight + dirReward * dirWeight + edgeReward * edgeWeight

        print(mapwidth, mapheight, goal_x, goal_y, distance, int(self.car.x),int(self.car.y), last_reward)

        if distance < 25:
            if swap == 1:
                print("Second Goal reached")
                goal_x = 885
                goal_y = 50
                swap = 2
            elif swap == 2:
                print("Third Goal reached")
                goal_x = 1055
                goal_y = 595
                swap = 0
            else:
                print("First Goal reached")
                goal_x = 177
                goal_y = 802
                swap = 1
        last_distance = distance

# Adding the painting tools

class MyPaintWidget(Widget):

    def on_touch_down(self, touch):
        global length, n_points, last_x, last_y
        with self.canvas:
            Color(0.8,0.7,0)
            d = 10.
            touch.ud['line'] = Line(points = (touch.x, touch.y), width = 10)
            last_x = int(touch.x)
            last_y = int(touch.y)
            n_points = 0
            length = 0
            sand[int(touch.x),int(touch.y)] = 1
            img = PILImage.fromarray(sand.astype("uint8")*255)
            img.save("./map/EndlessSand.jpg")

    def on_touch_move(self, touch):
        global length, n_points, last_x, last_y
        if touch.button == 'left':
            touch.ud['line'].points += [touch.x, touch.y]
            x = int(touch.x)
            y = int(touch.y)
            length += np.sqrt(max((x - last_x)**2 + (y - last_y)**2, 2))
            n_points += 1.
            density = n_points/(length)
            touch.ud['line'].width = int(20 * density + 1)
            sand[int(touch.x) - 10 : int(touch.x) + 10, int(touch.y) - 10 : int(touch.y) + 10] = 1

            
            last_x = x
            last_y = y

# Adding the API Buttons (clear, save and load)

class CarApp(App):

    def build(self):
        parent = Game()
        parent.serve_car()
        Clock.schedule_interval(parent.update, 1.0/60.0)
        self.painter = MyPaintWidget()
        clearbtn = Button(text = 'clear')
        savebtn = Button(text = 'save', pos = (parent.width, 0))
        loadbtn = Button(text = 'load', pos = (2 * parent.width, 0))
        clearbtn.bind(on_release = self.clear_canvas)
        savebtn.bind(on_release = self.save)
        loadbtn.bind(on_release = self.load)
        parent.add_widget(self.painter)
        parent.add_widget(clearbtn)
        parent.add_widget(savebtn)
        parent.add_widget(loadbtn)
        return parent

    def clear_canvas(self, obj):
        global sand
        self.painter.canvas.clear()
        sand = np.zeros((longueur,largeur))

    def save(self, obj):
        print("saving brain...")
        brain.save()
        plt.plot(scores)
        plt.show()

    def load(self, obj):
        print("loading last saved brain...")
        brain.load()

# Running the whole thing
if __name__ == '__main__':
    CarApp().run()
