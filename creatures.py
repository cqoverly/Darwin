import random
import copy

import kivy
kivy.require('1.6.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Ellipse, Color
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.properties import ObjectProperty, ReferenceListProperty,\
    NumericProperty



class Predator(Widget):
    # velocity_x = NumericProperty(0)
    # velocity_y = NumericProperty(0)
    # velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __init__(self,
                 *args, **kwargs):
        super(Predator, self).__init__(*args, **kwargs)
        self.shape_genes = kwargs.get('shape_genes', ('r', 'e'))
        self.color_genes = kwargs.get('color_genes', ('b', 'r'))
        self.offspring_genes = kwargs.get('offspring_genes', (5, 3))
        self.gender = random.choice(('M', 'F'))
        self.color = self.get_color()
        self.shape = self.get_shape()
        self.lifespan = random.randint(15000, 20000)  # orig: 9000, 12000
        self.hunger = 0
        self.age = 0
        self.size = (10, 10)
        self.draw()
        self.velocity_x = random.randint(-2,2)
        self.velocity_y = random.randint(-2,2)
        self.velocity = self.velocity_x, self.velocity_y

    def __str__(self):
        return str(self.__dict__)

    def get_color(self):
        if 'b' in self.color_genes:
            return (0, 0, 1)
        else:
            return (1, 0, 0)

    def get_shape(self):
        if 'r' in self.shape_genes:
            return 'Rectangle'
        else:
            return 'Ellipse'

    def draw(self):
        with self.canvas:
            Color(*self.color)
            if self.shape == "Rectangle":
                Rectangle(size=self.size, pos=self.pos)
            else:
                Ellipse(size=self.size, pos=self.pos)

    def start(self):
        pass

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos
        self.canvas.clear()
        self.draw()


class World(Widget):
    count = 0
    adam = ObjectProperty(None)
    eve = ObjectProperty(None)

    def random_position(self):
        return (random.randint(5, self.width-5),
                random.randint(5, self.height-5))

    def start_world(self):
        print self.size
        adam = Predator(pos=self.random_position(),
                        id='adam')
        adam.gender = 'M'
        self.add_widget(adam)
        eve = Predator(pos=self.random_position(),
                       id='eve')
        eve.gender = 'F'
        self.add_widget(eve)
        print adam, "\n", eve
        print adam.pos
        print eve.pos

    def update(self, dt):
        if self.count <= 600:
            if self.count % 10 == 0:
                for c in self.children:
                    if random.randint(1,6) == 3:
                        c.velocity_x = random.randint(-2, 2)
                        c.velocity_y = random.randint(-2, 2)
                        c.velocity = (c.velocity_x, c.velocity_y)
        else:
            self.count = 1
        if self.count < 1:
            print "Less than 1"
            print self.size
            self.count += 1
            self.start_world()
        # elif self.count == 1:
        #     print self.size
        #     self.start_world()
        #     self.count += 1
        #     print self.children
        for c in self.children:
            #  Check to see if creature hitting top of bottom of window.
            if c.top > self.height or c.y < self.y:
                c.velocity_y *= -1
            #  Check to see if creature is hetting left or right sede of window.
            if c.x < self.x or c.x + c.width > self.width:
                c.velocity_x *= -1
            c.velocity = c.velocity_x, c.velocity_y
            c.move()
        self.count += 1

    def mating(self, creatureA, creatureB):
        genders = (creatureA.gender, creatureB.gender)
        #  Make sure it's a M/F pairing.
        if 'F' not in genders or 'M' not in genders:
            pass
        else:
            #  Get female 
            f = [c for c in (creatureA, creatureB) if c.gender == 'F'][0]
            #  And male
            m = [c for c in (creatureA, creatureB) if c.gender == 'M'][0]                
            #  Choose which birth genes to use.
            spawn = random.choice(f.offspring_genes)
            for i in range(spawn):
                #  gather genes for children.
                colors = (random.choice(f.color_genes),
                          random.choice(m.color_genes))
                shape = (random.choice(f.shape_genes),
                         random.choice(m.shape_genes))
                offspring = (random.choice(f.offspring_genes),
                             random.choice(m.offspring_genes))
                pos = (random.randint(1, self.size))
                new_creature = Predator(pos=self.random_position())


class WorldApp(App):

        def build(self):
            world = World()
            Clock.schedule_interval(world.update, 1.0/20.0)
            return world


if __name__ == "__main__":
    WorldApp().run()

