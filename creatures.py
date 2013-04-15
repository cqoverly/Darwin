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
    color_dict = {'b': (0, 0, 1), 'r': (1, 0, 0)}

    def __init__(self,
                 *args, **kwargs):
        super(Predator, self).__init__(*args, **kwargs)
        self.shape_genes = kwargs.get('shape_genes', ('r', 'e'))
        self.color_genes = kwargs.get('color_genes', ('b', 'r'))
        self.offspring_genes = kwargs.get('offspring_genes', (1, 2))
        self.gender = random.choice(('M', 'F'))
        self.color = self.get_color()
        self.shape = self.get_shape()
        self.lifespan = random.randint(12000, 15000)  # orig: 9000, 12000
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
            return Predator.color_dict['b']
        elif 'r' in self.color_genes:
            return Predator.color_dict['r']
        else:
            return Predator.color_dict[self.color_genes[0]]

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
    mutation_count = 1

    def on_touch_down(self, touch):
        t = self.children
        reds = len([c for c in t if c.color == (1, 0, 0)])
        els = len([c for c in t if c.shape == 'Ellipse'])
        males = len([c for c in t if c.gender == 'M'])
        attrs = {'reds': reds,
                 'blues': len(t) - reds,
                 'els': els,
                 'rects': len(t) - els,
                 'males': males,
                 'females': len(t) - males,
                 'age_avg': sum([c.age for c in t])/float(len(t)),
                 'total': len(t)}
        print """
                Total: %(total)d
                Average Age: %(age_avg)0.2f
                Males: %(males)d / Females: %(females)d
                Blues: %(blues)d / Reds: %(reds)d
                Rectangles: %(rects)d / Ellipses: %(els)d
            """ % (attrs)

        super(World, self).on_touch_down(touch)

    def random_position(self):
        return (random.randint(21, self.width-21),
                random.randint(21, self.height-21))

    def start_world(self):
        with self.canvas:
            Color(1, 1, 1, .7)
            Rectangle(size=self.size, pos=self.pos)
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

        # Randomize movements for each predator instance
        if self.count <= 600:  # Overall movement time frame.
            #  Check for random movement every 10 frames.
            if self.count % 10 == 0:
                for c in self.children:
                    #  Change only occurs 1/6th of the time per 10 frames.
                    if random.randint(1,6) == 3:
                        c.velocity_x = random.randint(-2, 2)
                        c.velocity_y = random.randint(-2, 2)
                        # c.velocity = (c.velocity_x, c.velocity_y)
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
        be successful.  Mutations are handled on a random (and rare) basis.
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
                #  Get male
                m = [c for c in (creatureA, creatureB) if c.gender == 'M'][0]
                #  Choose which birth genes to use.
                spawn = random.choice(f.offspring_genes)
                for i in range(spawn):
                    #  gather genes for children.
                    colors = [random.choice(f.color_genes),
                              random.choice(m.color_genes)]

                    # check for color mutation
                    mutation = (random.randint(1, 50) == 5)
                    # If there is a mutation, generate mutant color
                    # and add it to the Predator.color_dict
                    if mutation:
                        curr_colors = Predator.color_dict.values()
                        hue = random.randint(0, 2)  # R, G, or B hue.
                        # value = random.randint(5, 10)/10.0
                        value = round(random.random(), 1)
                        if value == 0:
                            value += 0.1  # Make sure it has a value
                        # make mutable copy of gene to mutate
                        base_color = list(Predator.color_dict[colors[1]])
                        # Change gene
                        base_color[hue] = value
                        base_color = tuple(base_color)
                        # Add to color_dictionary if it doesn't exist.
                        # Only transfer the gene if it doesn't exist.
                        if base_color not in curr_colors:
                            gene_name = "M{0}".format(str(self.mutation_count))
                            Predator.color_dict[gene_name] = base_color
                            self.mutation_count += 1
                            print "MUTATION! Color: {0}".format(base_color)
                            colors[1] = gene_name

                    colors = tuple(colors)
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
            Clock.schedule_interval(world.update, 1.0/30.0)
            return world


if __name__ == "__main__":
    WorldApp().run()

