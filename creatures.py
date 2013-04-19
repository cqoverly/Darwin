import random
import copy

import kivy
kivy.require('1.6.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle, Ellipse, Color
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.properties import ObjectProperty, ReferenceListProperty,\
    NumericProperty
from kivy.core.audio import SoundLoader
from kivy.config import Config



Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '600')


# Load sound effects.
death_snd = SoundLoader.load('sounds/neck_snap-Vladimir-719669812.wav')
birth_snd = SoundLoader.load('sounds/Blop-Mark_DiAngelo-79054334.wav')
mutation_snd = SoundLoader.load('sounds/Child Scream-SoundBible.com-1951741114.wav')
info_snd = SoundLoader.load('sounds/Mario_Jumping-Mike_Koenig-989896458.wav')

# Fix sound volume issues.

class Predator(Widget):
    color_dict = {'b': (0, 0, 1), 'r': (1, 0, 0)}
    lifespan_factor = 1  # Controlled by ControlPanel.lifespan_ctl slider

    def __init__(self,
                 *args, **kwargs):
        super(Predator, self).__init__(*args, **kwargs)
        self.shape_genes = kwargs.get('shape_genes', ('r', 'e'))
        self.color_genes = kwargs.get('color_genes', ('b', 'r'))
        self.offspring_genes = kwargs.get('offspring_genes', (1, 2))
        self.gender = random.choice(('M', 'F'))
        # TODO: create @color_genes.setter for color and color_name
        # self.color = self.get_color()[0]
        # self.color_name = self.get_color()[1]
        self.shape = self.get_shape()
        self.lifespan = random.randint(12000, 15000)  # orig: 9000, 12000
        self.hunger = 0
        self.age = kwargs.get('age', 0)
        self.size = self.get_size()
        self.draw()
        self.velocity_x = random.randint(-2, 2)
        self.velocity_y = random.randint(-2, 2)
        self.velocity = self.velocity_x, self.velocity_y

    def __str__(self):


        try:

            return"""
                    Sex: {gender}  Lifespan: {lifespan}  Age {age}
                    Color Genes: {color_genes}  Shape Genes: {shape_genes}
                  """.format(**self.__dict__)
        except KeyError:
            return str(self.__dict__)

    @property
    def color_name(self):
        """
        Provides values for 2 attributes of Predator: color & color_name
        A tuple of two values is returned: (color, color_name)
        """
        if 'b' in self.color_genes:
            return 'b'
        elif 'r' in self.color_genes:
            return 'r'
        else:
            return self.color_genes[0]

    @property
    def color(self):
        return Predator.color_dict[self.color_name]

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

    def update_size(self):
        s = 0
        try:
            s = int(max(self.age / 200, 2))
        except ZeroDivisionError:
            s = s
        if self.gender == 'M':
            s *= .8  # Males are smaller.
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
        global death_snd
        lf = Predator.lifespan_factor
        curr_preds = len(self.parent.children)
        too_old = False
        if curr_preds > 70:
            if self.age > (self.lifespan * lf) * .7:
                too_old = True
        elif self.age > self.lifespan * lf:
            too_old = True
        if too_old:
            self.parent.remove_widget(self)
            death_snd.play()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            print self


class World(Widget):
    count = 0
    adam = ObjectProperty(None)
    eve = ObjectProperty(None)
    mutation_count = 1
    sim_started = False
    mutation_rate = 50
    lifespan_ratio = 1
    sim_speed = 35

    def random_position(self):
        return (random.randint(self.x+21, self.width-21),
                random.randint(self.y+21, self.height-21))

    def start_world(self):
        age = 2000
        print "Container size:", self.parent.size
        print "World size:", self.size
        for i in range(5):
            adam = Predator(pos=self.random_position(), age=age)
            adam.gender = 'M'
            self.add_widget(adam)
        for i in range(10):
                eve = Predator(pos=self.random_position(), age=age)
                eve.gender = 'F'
                self.add_widget(eve)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            global info_snd
            t = self.children
            reds = len([c for c in t if c.color == (1, 0, 0)])
            els = len([c for c in t if c.shape == 'Ellipse'])
            males = len([c for c in t if c.gender == 'M'])
            age_avg = 0
            try:
                age_avg = sum([c.age for c in t]) / float(len(t))
            except ZeroDivisionError:
                age_avg = 0
            attrs = {'reds': reds,
                     'blues': len(t) - reds,
                     'els': els,
                     'rects': len(t) - els,
                     'males': males,
                     'females': len(t) - males,
                     'age_avg': age_avg,
                     'total': len(t)}

            info_snd.volume = 0.0
            info_snd.play()
            info = """
                    Total: {total}
                    Average Age: {age_avg}
                    Males: {males} / Females: {females}
                    Blues: {blues} / Reds: {reds}
                    Rectangles: {rects} / Ellipses: {els}
                """.format(**attrs)
            print info
            self.parent.ctl_panel.update_info(attrs)
            active_colors = sorted(set([c.color_name for c in self.children]))
            d = Predator.color_dict
            print "Full color dict:", d
            curr_cgenes = dict((color_name, d.get(color_name))
                               for color_name in active_colors)
            print "Active colors:", str(curr_cgenes)
            print "Mutation rate:", self.mutation_rate
            print "Lifespan factor:", Predator.lifespan_factor
            print self.parent.snd_volume
            print info_snd.volume
            return True
        super(World, self).on_touch_down(touch)

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
        global birth_snd
        global mutation_snd
        curr_preds = len(self.children)

        #  Make sure it's a M/F pairing and both are old enough.
        if ('F' in sex and 'M' in sex) and (ages[0] > 2000 and ages[1] > 2000):
            #  Random chance of successful mating based on population.
            if curr_preds > 100:
                pop_factor = 1000000
            elif predators/15 > 6:
                pop_factor = 10000
            elif curr_preds/15 > 3:
                pop_factor = 150
            elif curr_preds/15 > 1:
                pop_factor = 50
            else:
                pop_factor = 20
            if random.randint(1, pop_factor) == 10:
                #  Get female
                f = [c for c in (creatureA, creatureB) if c.gender == 'F'][0]
                #  Get male
                m = [c for c in (creatureA, creatureB) if c.gender == 'M'][0]
                #  Choose which birth genes to use.
                spawn = random.choice(f.offspring_genes)
                sound = birth_snd
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

                    # check for color mutation
                    if self.mutation_rate >= 1:
                        mutation = (random.randint(1, self.mutation_rate) == 1)
                    else:
                        mutation = False
                    # If there is a mutation, generate mutant color
                    # and add it to the Predator.color_dict
                    if mutation:
                        sound = mutation_snd
                        # create a Mutator instance with new offspring
                        mutator = Mutator(new_creature)
                        # mutate one gene in the new offspring.
                        new_creature = mutator.mutate()

                    self.add_widget(new_creature)
                    sound.play()
                    print new_creature
                print """
                MATING! Babies: {0} / Total Predators: {1}
                """.format(spawn, len(self.children))

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
                    if random.randint(1, 6) == 3:
                        c.velocity_x = random.randint(-2, 2)
                        c.velocity_y = random.randint(-2, 2)
        else:
            self.count = 1
        if self.count == 2 and not self.sim_started:
            print "Less than 1"
            print self.size
            self.count += 1
            self.start_world()
            self.sim_started = True
        # Check all
        preds = [pred for pred in self.children if pred.__class__ == Predator]
        # for c in self.children:
        for c in preds:
            #  Check to see if creature hitting top of bottom of window.
            if c.top > self.height - 5 or c.y < self.y + 5:
                c.velocity_y *= -1
            #  Check to see if creature is hetting left or right sede of window.
            if c.x < self.x + 5 or c.x + c.width > self.x + self.width - 5:
                c.velocity_x *= -1
            c.velocity = c.velocity_x, c.velocity_y
            #  Check females for collisions.
            if c.gender == 'F':
                others = [o for o in self.children if o != c]
                for o in others:
                    if c.collide_widget(o) and o.gender == 'M':
                        self.mating(c, o)
            c.update_attrs()

        self.count += 1


class Mutator(object):
    """
    Creates a mutation instance which takes a particular creature in its
    constructor.

    Methods to pick genes, mutate them, and place them back into original
    are created.

    """

    def __init__(self, creature):
        self.creature = creature

    def mutate(self):

        # Function map for mutations based on gene types
        gene_dict = {
            'color_genes': self.mutate_color,
            'shape_genes': self.mutate_shape,
            'rotation_genes': self.mutate_rotation,
            'bias_genes': self.mutate_bias,
            'offspring_genes': self.mutate_offspringgenes
        }
        # Find the attributes that are genes.
        d = self.creature.__dict__
        genes = dict((g, d.get(g)) for g in d.keys() if 'genes' in g)
        # Randomly pick a gene type and call the correct method.
        to_mutate = random.choice(genes.items())
        gene_dict[to_mutate[0]]()
        # Send mutated creature back to caller (World.mating())
        return self.creature



    def mutate_color(self):

        # Reference to all current color genes.
        color_d = Predator.color_dict
        # Create a mutable list of the color genes.
        genes_temp = list(self.creature.color_genes)
        # Generate a new color (represents a mutation of a color gene)
        base_color = [0, 0, 0]
        for hue in range(3):  # R, G, or B hue.
            # value = random.randint(5, 10)/10.0
            value = round(random.random(), 1)
            if value == 0:
                value += 0.1  # Make sure it has a value
                # make mutable copy of gene to mutate
            # Change gene
            base_color[hue] = value
        new_color = tuple(base_color) # Cast to appropriate type.
        # Add to color_dictionary if it doesn't exist.
        curr_colors = color_d.values() # all colors in Predator.color_dict
        if new_color not in curr_colors:
            gene_name = "M{0}".format(str(World.mutation_count))
            color_d[gene_name] = new_color
            World.mutation_count += 1
            print """
                MUTATION! Color Name: {0}
                          Color: {1}
            """.format(gene_name, new_color)
            genes_temp[random.choice(range(2))] = gene_name
            genes = tuple(genes_temp)
            self.creature.color_genes = genes
        # If color already exists, get the color_name and pass
        # it into color_genes
        else:
            # Create a reverse color_dict to look up color name
            # of new_color.
            rev_dict = dict((item[1], item[0]) for item in color_d.items())
            genes_temp[random.choice(range(2))] = rev_dict[new_color]
            genes = tuple(genes_temp) # Cast to appropriate type.
            self.creature.color_genes = genes
        return

    def mutate_shape(self):
        print "SHAPE MUTATED"
        return

    def mutate_rotation(self):
        print "ROTATION MUTATED"
        return

    def mutate_bias(self):
        print "BIAS MUTATED"
        return

    def mutate_offspringgenes(self):
        print "OFFSPRING GENES MUTATED"

        return



class ControlPanel(BoxLayout):
    lifespan_ctl = ObjectProperty(None)
    mating_ctl = ObjectProperty(None)
    speed_ctl = ObjectProperty(None)
    mutation_ctl = ObjectProperty(None)
    info_disp = ObjectProperty(None)

    def update_info(self, info_dict):
        """
        Updates the info in the info window after an on_touch_down event in the World instance.
        """
        self.info_disp.text = """
Total: {total}
Average Age: {age_avg}
Males: {males} / Females: {females}
Blues: {blues} / Reds: {reds}
Rects: {rects} / Ellipses: {els}
""".format(**info_dict)

    def read_slider(self, slider):

        if slider == 'mutation_ctl':
            World.mutation_rate = int(self.mutation_ctl.value)
        elif slider == 'lifespan_ctl':
            Predator.lifespan_factor = int(self.lifespan_ctl.value)
        elif slider == 'speed_ctl':
            World.sim_speed = int(self.speed_ctl.value)


class Container(BoxLayout):
    world = ObjectProperty(None)
    ctl_panel = ObjectProperty(None)

    snd_volume = 0

    def update(self, dt):
        self.world.update(dt)


class DarwinApp(App):

    def build(self):
        rate = 30.0
        root = Container()
        Clock.schedule_interval(root.update, 1.0 / World.sim_speed)
        return root


if __name__ == "__main__":
    DarwinApp().run()

