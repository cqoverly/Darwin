import random
import copy
from math import pi

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
sl = SoundLoader
death_snd = sl.load('sounds/neck_snap-Vladimir-719669812.wav')
birth_snd = sl.load('sounds/Pew_Pew-DKnight556-1379997159.wav')
mutation_snd = sl.load('sounds/Child Scream-SoundBible.com-1951741114.wav')
info_snd = sl.load('sounds/Mario_Jumping-Mike_Koenig-989896458.wav')
ate_snd = sl.load('sounds/Belch-Kevan-136688254.wav')

# TODO: Fix sound volume issues.


class Predator(Widget):
    """
    The Predator class provides the main creature instance. (Prey class may be
    implemented later.)

    Gene Dominance:
        Shape: Rectangle (r) over Ellipse (e)
        Color: Blue (b) over Red (r) over mutated colors.
               If both color_genes are mutated, idx[0] becomes dominant.
        Offspring: No dominant gene. 50/50 change at time of breeding.
        Gender: No dominant gene. 50/50 change at time of inception.

    Instances are updated with each clock cycle.

    self.max_size is used for initial growth. Once instance's size = max_size
    the size will no longer be updated and it is full grown.

    self.lifespan sets the number of clock cycles the instance will live.
    This may be shortened programatically if populations get large. Or a male
    may have life cut short if eaten by a female. self.lifespan may also be
    modified by user via the lifespan control slider.

    """

    # The color_dict holds all colors present at time present. Mutated colors
    # are added as they occur. The dict is used for to determing rgb for
    # drawing purposes.
    color_dict = {'b': (0, 0, 1), 'r': (1, 0, 0)}
    lifespan_factor = 1  # Controlled by ControlPanel.lifespan_ctl slider
    death = False

    def __init__(self,
                 *args, **kwargs):
        super(Predator, self).__init__(**kwargs)
        self.shape_genes = kwargs.get('shape_genes', (['r', [10, 10]],
                                                      ['e', [0, 360]]))
        self.color_genes = kwargs.get('color_genes', ('b', 'r'))
        self.offspring_genes = kwargs.get('offspring_genes', (1, 2))
        self.gender = random.choice(('M', 'F'))
        # self.shape = self.get_shape()
        self.lifespan = random.randint(12000, 15000)  # orig: 9000, 12000
        self.hunger = 0
        self.age = kwargs.get('age', 0)
        self.size = self.get_size()
        self.draw()  # place the initial instance on canvas.
        self.velocity_x = random.randint(-2, 2)
        self.velocity_y = random.randint(-2, 2)
        self.velocity = self.velocity_x, self.velocity_y
        self.eaten = False  # Flag for use during update.
        self.stuck = 0  # Counter to monitor how long instance on border.

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
        """
        color property determines the actual rgb value of the instance's
        color, used to draw the instance on the canvas.
        """
        return Predator.color_dict[self.color_name]

    @property
    def area(self):
        if self.shape == 'Rectangle':
            return self.size[0] * self.size[1]
        elif self.shape == 'Ellipse':
            try:
                arc = (self.angle_end - self.angle_start) / 360.0
            except AttributeError:
                arc = 1.0
            radius = self.size[0] / 2
            area = (pi * radius**2) * arc
            return round(area, 2)
        else:
            print "There's a shape in here that shouldn't exist!"

    @property
    def max_size(self):
        """
        The shape definition. of an instance is at idx[1] of each shape gene.
        For example: shape_genes = (['r', [10, 12]], ['e', [0, 270]])
        In the above example, the instance has 2 shape genes, one for a
        rectangle with amax_size of width 10 and height 12. The second gene
        is for an ellipse, with the shape definition determining its arc
        instead of dimensions. Ellipse dimensions default to a 10 diameter for
        females and an 8 diameter for males. The rectangle ('r') gene is
        dominant.
        """
        if self.shape == 'Rectangle':
            # Pull the gene to use, if both are 'r' then use idx 0, making
            # the size in idx 0 dominant.
            genes = [g for g in self.shape_genes if g[0] == 'r'][0]
            w = genes[1][0]
            h = genes[1][1]
        else:
            w = 10
            h = 10
        if self.gender == 'M':  # Make the males 80% of females.
            w *= 0.8
            h *= 0.8
        return (round(w), round(h))

    @property
    def shape(self):
        """
        'r' is dominant. So if it is in either gene, it's a rectangle.
        """

        if 'r' in (self.shape_genes[0][0], self.shape_genes[1][0]):
            return 'Rectangle'
        else:
            return 'Ellipse'

    # Using @property does not work in this context as it raises an exception
    # that I don't remember, that is set off in Predator.update_attributes.
    def get_size(self):
        """
        Used to create initial size of instance if none given.
        """

        width = 2
        height = 2
        if self.gender == 'M':
            # Males are smaller.
            width = int(width * 0.8)
            height = int(height * 0.8)
        return width, height

    def draw(self):
        """
        The draw() method is called every time the creature needs to be
        updated for movement, size, or initial creation.
        """

        with self.canvas:
            Color(*self.color)
            if self.shape == "Rectangle":
                Rectangle(size=self.size, pos=self.pos)
            else:
                Ellipse(size=self.size, pos=self.pos)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    def update_size(self):
        """
        The update_size method is used to grow the instance to its full size
        over time. Once the instance is full grown, the method is no longer
        used in the update_attrs method.
        """

        w = 0
        h = 0
        w_growth = self.age / (2000 / self.max_size[0])
        h_growth = self.age / (2000 / self.max_size[1])

        if self.size[0] < self.max_size[0]:
            try:
                w = int(max(w_growth, 2))
            except ZeroDivisionError:
                w = w
        if self.size[1] < self.max_size[1]:
            try:
                h = int(max(h_growth, 2))
            except ZeroDivisionError:
                h = h
        if self.gender == 'M':
            w *= 0.8
            h *= 0.8

        w = int(min(int(w), self.max_size[0]))
        h = int(min(int(h), self.max_size[1]))
        return w, h

    def update_attrs(self):
        """
        Called from World.update, which is the main update for the simulation,
        handled by Clock,schedule_interval().
        """
        self.age += 1
        # Update size until full grown.
        if self.size[0] < self.max_size[0] and self.size[1] < self.max_size[1]:
            self.size = self.update_size()
        self.move()
        # Clear canvas of previous position.
        self.canvas.clear()
        # Draw instance in new posision.
        self.draw()
        # Check if instance is still alive. And handle if not.
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
        if self.eaten or self.stuck == 600:
            death_snd.play()
            self.parent.remove_widget(self)
            return
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
            # death_snd.play()
            Predator.death = True

    def on_touch_down(self, touch):
        """
        Gather information about an instance and print to stdout, which
        is terminal by default.
        """

        if self.collide_point(*touch.pos):
            print self
            print "Predator's Position:", self.pos
            print "Current Size:", self.size
            print "Max Size:", self.max_size
            print "Area:", self.area


class World(Widget):
    """
    The Worlds class is used to create the main environment for the
    simulated objects.
    """
    top_bound = ObjectProperty(None)
    bottom_bound = ObjectProperty(None)
    left_bound = ObjectProperty(None)
    right_bound = ObjectProperty(None)

    count = 0  # Used the sequence initial creation steps.
    mutation_count = 1
    sim_started = False
    mutation_rate = 50  # can be adjusted via control panel slider.
    total_eaten = 0  # For debugging purposes.

    def __init__(self, **kwargs):
        super(World, self).__init__(**kwargs)
        self.speed = 35.0
        # Create a clock instance that calls self.update every cycle.
        self.clock = Clock.schedule_interval(self.update, 1/self.speed)

    def update_clock(self, rate):
        clock_rate = round(float(rate), 1)
        # self.clock must be released to keep multiple instances
        # from being created, multiplying update intervals by number of
        # clock instances.
        self.clock.release()
        self.clock = Clock.schedule_interval(self.update, 1/clock_rate)

    def random_position(self):
        """
        Method is used to place initial instances of Predator during
        start_world method.
        """
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

    def get_preds(self):
        return [p for p in self.children if isinstance(p, Predator)]

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
        super(World, self).on_touch_down(touch)
        preds = self.get_preds()
        if self.collide_point(*touch.pos):
            global info_snd
            reds = len([c for c in preds if c.color == (1, 0, 0)])
            blues = len([c for c in preds if c.color == (0, 0, 1)])
            els = len([c for c in preds if c.shape == 'Ellipse'])
            males = len([c for c in preds if c.gender == 'M'])
            age_avg = 0
            try:
                age_avg = round(sum([c.age for c in preds]) / float(len(preds)), 2)
            except ZeroDivisionError:
                age_avg = 0
            attrs = {'reds': reds,
                     'blues': blues,
                     'mut_cols': len(preds) - (blues + reds),
                     'els': els,
                     'rects': len(preds) - els,
                     'males': males,
                     'females': len(preds) - males,
                     'age_avg': age_avg,
                     'total': len(preds),
                     'eaten': self.total_eaten}

            info_snd.volume = 0
            info_snd.play()
            info = """
                    Total: {total}
                    Average Age: {age_avg}
                    Males: {males} / Females: {females}
                    Blues: {blues} / Reds: {reds}
                    Rectangles: {rects} / Ellipses: {els}
                    M eaten by F: {eaten}
                """.format(**attrs)
            print info
            self.parent.ctl_panel.update_info(attrs)
            active_colors = sorted(set([c.color_name for c in preds]))
            d = Predator.color_dict
            print "Full color dict:", d
            curr_cgenes = dict((color_name, d.get(color_name))
                               for color_name in active_colors)
            print "Active colors:", str(curr_cgenes)
            print "Mutation rate:", self.mutation_rate
            print "Lifespan factor:", Predator.lifespan_factor
            print self.parent.snd_volume
            print info_snd.volume
            print info_snd.__class__
            return True

    def ate_him(self, f, m):
        """
        Determines whether a female eats a male after mating or not.
        """
        # Will only eat males 70% of own size or smaller.
        if f.area * 0.5 >= m.area:
            # Channce of f catching male.
            if random.randint(1, 2) == 1:
                self.total_eaten += 1
                return True
            else:
                return False

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
        global ate_snd
        preds = self.get_preds()
        curr_preds = len(preds)
        mating_bias = 1

        #  Make sure it's a M/F pairing and both are old enough.
        if ('F' in sex and 'M' in sex) and (ages[0] > 2000 and ages[1] > 2000):
            # Get female
            f = [c for c in (creatureA, creatureB) if c.gender == 'F'][0]
            # Get male
            m = [c for c in (creatureA, creatureB) if c.gender == 'M'][0]
            # Random chance of successful mating based on population.
            # Larger pop_factor means smaller chance of successful mating.
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
            # Check for bias, Females prefer males who are
            # smaller than themselvels.
            if f.area * 0.9 <= m.area:
                # Find mating bias, ensure it is at least 1
                mating_bias = max((m.area - f.area)/f.area, 1)
                # Multiply pop_factor based on mating bias. This will make
                # a successful mating less likely.
                pop_factor *= mating_bias
            # Check for a successful mating. 1 in pop_factor chance.
            if random.randint(1, pop_factor) == 10:
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
                    print new_creature
                ate = self.ate_him(f, m)
                if ate:
                    m.eaten = True
                    ate_snd.play()
                sound.play()

    def update(self, dt):
        """
        World.update is the main looping function for the program.
        This function check at each frame interval to see what events occur.
        Primarily, it checks calls creature udate methods to determine
        creature life events, as well as checks for collisions between
        creatures, at which point interaction events occur, such as potential
        matings and births.
        """

        global death_snd
        preds = self.get_preds()
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
        # Check Predator instances for position relative to border of World.
        for c in preds:
            #  Check to see if creature hitting top of bottom of window.
            if c.collide_widget(self.top_bound) or \
                    c.collide_widget(self.bottom_bound):
                if c.y < self.y + 6:
                    c.y = self.y + 7
                elif c.y + c.height > self.y + self.height - 6:
                    c.y = self.y + self.height - 7 - c.height
                c.velocity_y *= -1
                c.stuck += 1
            #  Check to see if creature is hitting left or right side of window.
            #  Move creature inbounds if necessary.
            elif c.collide_widget(self.left_bound) or \
                    c.collide_widget(self.right_bound):
                if c.x < self.x + 6:
                    c.x = self.x + 7
                elif c.x + c. width > self.x + self.width - 6:
                    c.x = self.x + self.width - 7 - c.width
                c.velocity_x *= -1
                c.stuck += 1
            else:
                c.stuck = 0  # Not, stuck, reset stuck attr.
            c.velocity = c.velocity_x, c.velocity_y
            #  Check females for collisions.
            if c.gender == 'F':
                males = [o for o in preds if o.gender != 'F']
                for o in males:
                    if c.collide_widget(o):  # and o.gender == 'M':
                        self.mating(c, o)
            c.update_attrs()
            if Predator.death:
                Predator.death = False
                death_snd.play()
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
            genes = tuple(genes_temp)  # Cast to appropriate type.
            self.creature.color_genes = genes
        return

    def mutate_shape(self):
        to_mutate = random.choice(self.creature.shape_genes)
        if to_mutate[0] == 'r':
            size_attr = random.choice(range(2))
            mutation = random.choice(range(-3, 4))
            print "Mutating gene:", to_mutate[1]
            to_mutate[1][size_attr] += mutation
            if to_mutate[1][size_attr] < 3:
                to_mutate[1][size_attr] = 3
            if to_mutate[1][size_attr] > 16:
                to_mutate[1][size_attr] = 16

            print self.creature.shape_genes
        else:
            print "Ellipse gene mutated"

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
M Eaten by F: {eaten}
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
    """
    Container creates the root widget for the simulation.
    """
    world = ObjectProperty(None)
    ctl_panel = ObjectProperty(None)
    snd_volume = 0


class DarwinApp(App):
    # rate = 30

    def build(self):
        root = Container()
        return root


if __name__ == "__main__":

    DarwinApp().run()
