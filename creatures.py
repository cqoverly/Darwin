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



Config.set('graphics', 'width', '1136')
Config.set('graphics', 'height', '640')


# Load sound effects.
death_snd = SoundLoader.load('sounds/neck_snap-Vladimir-719669812.wav')
birth_snd = SoundLoader.load('sounds/Pew_Pew-DKnight556-1379997159.wav')
mutation_snd = SoundLoader.load('sounds/Child Scream-SoundBible.com-1951741114.wav')
info_snd = SoundLoader.load('sounds/Mario_Jumping-Mike_Koenig-989896458.wav')

# Fix sound volume issues.

class Predator(Widget):
    color_dict = {'b': (0, 0, 1), 'r': (1, 0, 0)}
    lifespan_factor = 1  # Controlled by ControlPanel.lifespan_ctl slider

    def __init__(self,
                 *args, **kwargs):
        super(Predator, self).__init__(**kwargs)
        self.shape_genes = kwargs.get('shape_genes', ('r', 'e'))
        self.color_genes = kwargs.get('color_genes', ('b', 'r'))
        self.offspring_genes = kwargs.get('offspring_genes', (1, 2))
        self.gender = random.choice(('M', 'F'))
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
                    Offspring Genes: {offspring_genes}
                  """.format(**self.__dict__)
        except KeyError:
            return str(self.__dict__)

    @property
    def color_name(self):
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

    @property
    def rotation(self):
        return min(self.rotation_genes)

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
        """
        Called from World.update, which is the main update for the simulation,
        handled by Clock,schedule_interval().
        """
        sex = self.gender
        self.age += 1
        # Update size until full grown.
        if (sex == 'F' and self.size[0] < 10) or\
           (sex == 'M' and self.size[0] < 8):
            self.update_size()
        self.move()
        # Clear canvas of previous position.
        self.canvas.clear()
        # Draw instance in new posision.
        self.draw()
        self.is_dead()

    def is_dead(self):
        """
        Method run each frame, checks if a Predator instance has reached
        its lifespan. Population factors are taken into account to help
        with over-populating the sim.

        Predator.life_factor is controlled via a user-controlled slider
        which allows user a large amount of control over lifespan,
        increasing it by as much as 100%, or decreasing it all the way to zero,
        which kills off population.
        """
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
    """
    The Worlds class is used to create the main environment for the
    simulated objects.
    """
    count = 0
    mutation_count = 1
    sim_started = False
    mutation_rate = 50
    # lifespan_ratio = 1

    def __init__(self, **kwargs):
        super(World, self).__init__(**kwargs)
        self.speed = 35.0
        self.clock = Clock.schedule_interval(self.update, 1/self.speed)

    def update_clock(self, rate):
        rate = round(float(rate), 1)
        self.clock.release()
        self.clock = Clock.schedule_interval(self.update, 1/rate)

    def random_position(self):
        return (random.randint(self.x+21, self.width-31),
                random.randint(self.y+21, self.height-31))

    def start_world(self):
        """
        Populates world with initial creatures.
        10 Females
        5 Males

        All creatures are the default types, though default gender in
        Predator.__init__ is random.choice('M', 'F').  For this reason it is
        mandatory to set gender manually after each is instantiated.

        Positions are set randomly through a World.random_position
        method that attempts to ensure creatures are not created right on the
        border of the World environment, which can cause a bug in which the
        movement algorithm creates a situation where the Preadator instance
        becomes such on the border.
        """
        age = 2000
        print "Container size:", self.parent.size
        print "World size:", self.size
        print self.clock.__dict__
        for i in range(5):
            adam = Predator(pos=self.random_position(),
                            age=random.randint(1000, 2000))
            adam.gender = 'M'
            self.add_widget(adam)
        for i in range(10):
                eve = Predator(pos=self.random_position(),
                               age=random.randint(1000, 2000))
                eve.gender = 'F'
                self.add_widget(eve)

    def on_touch_down(self, touch):
        """
        Override of on_touch_down method for use within the boundaries of the
        World widget instance.

        Generates a status update in the terminal, as well as a more general
        info update into the ControlPanel instance's info_display text window.

        Terminal info used for debugging purposes only.

        If the touch does not occure in the World instance boundaries, the
        original on_touch_down_method is called.
        """
        if self.collide_point(*touch.pos):
            global info_snd
            t = self.children
            reds = len([c for c in t if c.color == (1, 0, 0)])
            blues = len([c for c in t if c.color == (0, 0, 1)])
            els = len([c for c in t if c.shape == 'Ellipse'])
            males = len([c for c in t if c.gender == 'M'])
            age_avg = 0
            try:
                age_avg = round(sum([c.age for c in t]) / float(len(t)), 2)
            except ZeroDivisionError:
                age_avg = 0
            attrs = {'reds': reds,
                     'blues': blues,
                     'mut_cols': len(t) - (blues + reds),
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
        be successful.  Mutations are handled on a random (and rare) basis,
        though the rate can be made more or less frequent through use of the
        ControlPanel.mutation_ctl slider in the user interface.

        For mutations, a Mutator instance is created with a Predator instance
        as it's sole constructor aargument. Mutation of genes is handled
        within the Mutator class methods where the Predator instance's
        attributes are changed and then the instance sent back to be added
        to the World widget.
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
                males = [o for o in self.children if o.gender != 'F']
                for o in males:
                    if c.collide_widget(o):  # and o.gender == 'M':
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
        """
        Generates a new noramlize rgb color combination. After new color
        is created, method checks to see if the combination already exists
        in the Predator.color_dict:

            If color combination has not yet occurred:
                A new color_name is generated for the combination,
                a key with the name is created in the Predator.color_dict,
                and the key is given the value of the new color combination.
                Then the color_name is passed into either the first or
                second gene in the gene pair and set to the Predator
                instance's color_genes attribute.

            If color combination has already occurred in the sim:
                A reverse dict is created from the color_dict, the combination
                is used as a key to find the name of the color.  Then the
                color_name is passed into either the first or second gene
                in the gene pair and set to the Predator instance's
                color_genes attribute.
        """

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
        new_color = tuple(base_color)  # Cast to appropriate type.
        # Add to color_dictionary if it doesn't exist.
        curr_colors = color_d.values()  # all colors in Predator.color_dict
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

    def mutate_bias(self):
        print "BIAS MUTATED"
        return

    def mutate_offspringgenes(self):
        """
        Mutation method that randomly changes one of a gene pair in a
        Predator instance's offspring_genes. The actual number of offspring
        is still selected at random from the female's offspring gene set,
        so does sim does not use these genes in a dominant or recessive
        manner.
        """
        temp_genes = list(self.creature.offspring_genes)
        idx = random.choice(range(2))
        old_value = temp_genes[idx]
        new_value = random.choice((max(old_value-1, 0), old_value+1))
        temp_genes[idx] = new_value
        self.creature.offspring_genes = tuple(temp_genes)

        print "NEW OFFSPRING GENES:", self.creature.offspring_genes

        return



class ControlPanel(BoxLayout):
    """
    The ControlPanel is used to generate the main uer interface for the
    application.

    Controls created are:
        lifespan_ctl:
                Slider that sets Predator.lifespan_factor.
                The Predator.lifespan factor raises or decreases
                a Predator instance's base lifespan set in its
                lifespan attribute.

        mating_ctl:
                Used to increase of decrease the possibility of
                a successful mating.

        speed_ctl:
                Used to increase of decrease the speed of the
                simulation.

        mutation_ctl:
                Used to increase or decrease the rate of mutations
                when a successful mating occurs.
    """
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
Other Colors: {mut_cols}
Rects: {rects} / Ellipses: {els}
""".format(**info_dict)

    def read_slider(self, slider):

        if slider == 'mutation_ctl':
            World.mutation_rate = int(self.mutation_ctl.value)
        elif slider == 'lifespan_ctl':
            Predator.lifespan_factor = int(self.lifespan_ctl.value)/100.0
        elif slider == 'speed_ctl':
            rate = int(self.speed_ctl.value)
            self.parent.world.speed = int(self.speed_ctl.value)
            self.parent.world.update_clock(rate)



class Container(BoxLayout):
    world = ObjectProperty(None)
    ctl_panel = ObjectProperty(None)
    snd_volume = 0


class DarwinApp(App):
    rate = 30

    def build(self):
        root = Container()
        return root


if __name__ == "__main__":

    DarwinApp().run()

