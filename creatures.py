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
        self.offspring_genes = kwargs.get('offspring_genes', (1, 2))
        self.gender = random.choice(('M', 'F'))
        self.color = self.get_color()
        self.shape = self.get_shape()
        self.lifespan = random.randint(15000, 20000)  # orig: 9000, 12000
        self.hunger = 0
        self.age = 0
        self.size = self.get_size()
        self.draw()
        self.velocity_x = random.randint(-2, 2)
        self.velocity_y = random.randint(-2, 2)
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

    def get_size(self):
        s = 2
        if self.gender == 'M':
            s = int(s * .8)  # Males are smaller.
        return (s, s)

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
        # self.canvas.clear()
        # self.draw()

    def update_size(self):
        s = 0
        try:
            s = int(max(self.age / 200, 2))
        except ZeroDivisionError:
            s = s
        if self.gender == 'M':
            s = s * .8  # Males are smaller.
        self.size = (s, s)

    def update_attrs(self):
        sex = self.gender
        self.age += 1
        if (sex == 'F' and self.size[0] < 10) or\
           (sex == 'M' and self.size[0] < 8):
            self.update_size()
        self.move()
        self.canvas.clear()
        self.draw()
        self.is_dead()

    def is_dead(self):
        if self.age > self.lifespan:
            self.parent.remove_widget(self)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            print self
        super(Predator, self).on_touch_down(touch)



class World(Widget):
    count = 0
    adam = ObjectProperty(None)
    eve = ObjectProperty(None)

    def random_position(self):
        return (random.randint(21, self.width-21),
                random.randint(21, self.height-21))

    def start_world(self):
        print self.size
        for i in range(5):
            adam = Predator(pos=self.random_position(),
                            id='adam')
            adam.gender = 'M'
            self.add_widget(adam)
            eve = Predator(pos=self.random_position(),
                           id='eve')
            eve.gender = 'F'
            self.add_widget(eve)


    def update(self, dt):
        """
        World.update is the main looping function for the program.
        This function check at each frame interval to see what events occur.
        Primarily, it checks calls creature udate methods to determine
        creature life events, as well as checks for collisions between
        creatures, at which point interaction events occur, such as potential
        matings and births.
        """
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
            #  Check females for collisions.
            if c.gender == 'F':
                others = [p for p in self.children if p != c]
                for p in others:
                    if c.collide_widget(p) and p.gender == 'M':
                        self.mating(c, p)
            c.update_attrs()

        self.count += 1

    def mating(self, creatureA, creatureB):
        """
        Method sets ability to mate and the chance that mating will occur and
        be successful.
        """

        spawn = 0
        pop_factor = 0
        sex = (creatureA.gender, creatureB.gender)
        ages = (creatureA.age, creatureB.age)
        predators = len(self.children)  # Number of living predators

        #  Make sure it's a M/F pairing and both are old enough.
        if ('F' in sex and 'M' in sex) and (ages[0] > 2000 and ages[1] > 2000):
            #  Random chance of successful mating
            if predators/10 > 7:
                pop_factor = 10000
            elif len(self.children)/10 > 4:
                pop_factor = 150
            else:
                pop_factor = 50
            if random.randint(1, pop_factor) == (10):
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
                    shapes = (random.choice(f.shape_genes),
                              random.choice(m.shape_genes))
                    offspring = (random.choice(f.offspring_genes),
                                 random.choice(m.offspring_genes))
                    new_creature = Predator(pos=f.pos,
                                            shape_genes=shapes,
                                            color_genes=colors,
                                            offspring_genes=offspring)
                    self.add_widget(new_creature)
                    print new_creature
                print """
                MATING! Babies: {0} / Total Predators: {1}
                """.format(spawn, len(self.children))


class WorldApp(App):

        def build(self):
            world = World()
            Clock.schedule_interval(world.update, 1.0/20.0)
            return world


if __name__ == "__main__":
    WorldApp().run()

