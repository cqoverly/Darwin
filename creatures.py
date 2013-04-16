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
        self.color = self.get_color()[0]
        self.color_name = self.get_color()[1]
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

        try:
            return"""
                    Sex: {gender}  Lifespan: {lifespan}  Age {age}
                    Color: {color}  Color Name: {color_name} Shape: {shape}
                    Color Genes: {color_genes}  Shape Genes: {shape_genes}
                  """.format(**self.__dict__)
        except KeyError:
            return str(self.__dict__)

    def get_color(self):
        if 'b' in self.color_genes:
            return (Predator.color_dict['b'], 'b')
        elif 'r' in self.color_genes:
            return (Predator.color_dict['r'], 'r')
        else:

            return (Predator.color_dict[self.color_genes[0]],
                    self.color_genes[0])

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
        super(Predator, self).on_touch_down(touch)


class World(Widget):
    count = 0
    adam = ObjectProperty(None)
    eve = ObjectProperty(None)
    mutation_count = 1
    sim_started = False
    mutation_rate = 50
    lifespan_ratio = 1

    def random_position(self):
        return (random.randint(self.x+21, self.width-21),
                random.randint(self.y+21, self.height-21))

    def start_world(self):
        print self.size
        for i in range(5):
            adam = Predator(pos=self.random_position(),
                            id='adam')
            adam.gender = 'M'
            self.add_widget(adam)
        for i in range(10):
                eve = Predator(pos=self.random_position(),
                               id='eve')
                eve.gender = 'F'
                self.add_widget(eve)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            global info_snd
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
            curr_cgenes = dict((color, d.get(color)) for color in active_colors)
            print str(curr_cgenes)
            print "Mutation rate:", self.mutation_rate

        super(World, self).on_touch_down(touch)

    def mating(self, creatureA, creatureB):
        """
        Method sets ability to mate and the chance that mating will occur and
        be successful.  Mutations are handled on a random (and rare) basis.
        """
# TODO: Pull method too deal with mutation separately, and make it not
# creature specific so it can be used with any set of genes in any creature.
# Also, it should be made to deal with multiple sets of genes, returning
# a mutatated gene for each attribute addressed my the genes in a gene list.
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
            #  Random chance of successful mating
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
            if random.randint(1, pop_factor) == (10):
                #  Get female
                f = [c for c in (creatureA, creatureB) if c.gender == 'F'][0]
                #  Get male
                m = [c for c in (creatureA, creatureB) if c.gender == 'M'][0]
                #  Choose which birth genes to use.
                spawn = random.choice(f.offspring_genes)
                sound = birth_snd
                for i in range(spawn):
                    #  gather genes for children.
                    colors = [random.choice(f.color_genes),
                              random.choice(m.color_genes)]

                    # check for color mutation
                    if self.mutation_rate >= 1:
                        mutation = (random.randint(1, self.mutation_rate) == 1)
                    else:
                        mutation = False
                    # If there is a mutation, generate mutant color
                    # and add it to the Predator.color_dict
                    if mutation:
                        curr_colors = Predator.color_dict.values()
                        base_color = [0, 0, 0]
                        for hue in range(3):  # R, G, or B hue.
                            # value = random.randint(5, 10)/10.0
                            value = round(random.random(), 1)
                            if value == 0:
                                value += 0.1  # Make sure it has a value
                            # make mutable copy of gene to mutate
                            # Change gene
                            base_color[hue] = value
                        base_color = tuple(base_color)
                        # Add to color_dictionary if it doesn't exist.
                        # Only transfer the gene if it doesn't exist.
                        if base_color not in curr_colors:
                            sound = mutation_snd
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
            if c.top > self.height or c.y < self.y:
                c.velocity_y *= -1
            #  Check to see if creature is hetting left or right sede of window.
            if c.x < self.x or c.x + c.width > self.width:
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

class ControlPanel(BoxLayout):
    lifespan_ctl = ObjectProperty(None)
    mating_ctl = ObjectProperty(None)
    sim_speed = ObjectProperty(None)
    mutation_ctl = ObjectProperty(None)
    info_disp = ObjectProperty(None)

    def on_touch_down(self, touch):
        for wid in [self.lifespan_ctl, self.mutation_ctl]:
            if wid.collide_point(*touch.pos):
                touch.ud['control'] = wid
        super(ControlPanel, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.ud.get('control') == self.mutation_ctl:
            rate = self.mutation_ctl.value_normalized * self.mutation_ctl.max
            World.mutation_rate = int(rate)
        elif touch.ud.get('control') == self.lifespan_ctl:
            Predator.lifespan_factor = self.lifespan_ctl.value/100
            print Predator.lifespan_factor

    def update_info(self, info_dict):

        self.info_disp.text = """
Total: {total}
Average Age: {age_avg}
Males: {males} / Females: {females}
Blues: {blues} / Reds: {reds}
Rects: {rects} / Ellipses: {els}
""".format(**info_dict)




class Container(BoxLayout):
    world = ObjectProperty(None)
    ctl_panel = ObjectProperty(None)

    def update(self, dt):
        self.world.update(dt)



class DarwinApp(App):

        def build(self):
            rate = 30.0
            darwin = Container()
            Clock.schedule_interval(darwin.update, 1.0/rate)
            return darwin


if __name__ == "__main__":
    DarwinApp().run()

