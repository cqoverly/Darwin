"""
This module handles mutation of genes, passing back the mutated gene to the
original caller.
"""

import random
import creatures
from creatures import Predator



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
        gene_dict = {
            'color_genes': self.mutate_color,
            'shape_genes': self.mutate_shape,
            'rotation_genes': self.mutate_rotation,
            'bias_genes': self.mutate_bias,
            'offspring_genes': self.mutate_offspringgenes
        }

        d = self.creature.__dict__
        # get dict of gene attributes from creature.__dict__
        genes = dict((g, d.get(g)) for g in d.keys() if 'genes' in g)
        to_mutate = random.choice(genes.items())
        print to_mutate
        new_gene = gene_dict[to_mutate[0]]()
        # self.creature.__dict__[to_mutate[0]] = new_gene
        return self.creature



    def mutate_color(self):
        color_d = Predator.color_dict
        genes_temp = list(self.creature.color_genes)
        curr_colors = color_d.values()
        print "In mutate_color curr_colors:", curr_colors
        base_color = [0, 0, 0]
        for hue in range(3):  # R, G, or B hue.
            # value = random.randint(5, 10)/10.0
            value = round(random.random(), 1)
            if value == 0:
                value += 0.1  # Make sure it has a value
                # make mutable copy of gene to mutate
            # Change gene
            base_color[hue] = value
        new_color = tuple(base_color)
        # Add to color_dictionary if it doesn't exist.
        if new_color not in curr_colors:
            gene_name = "M{0}".format(str(creatures.World.mutation_count))
            color_d[gene_name] = new_color
            print "In Mutator 64:", Predator.color_dict
            creatures.World.mutation_count += 1
            print "MUTATION! Color: {0}".format(new_color)
            genes_temp[random.choice(range(2))] = gene_name
            genes = tuple(genes_temp)
            self.creature.color_genes = genes
            # self.creature.color = creatures.Predator.color_dict[gene_name]
            # self.creature.color_name = gene_name
            Predator.add_color(gene_name, new_color)
        # If color already exists, get the color_name and pass it in color_gene
        else:
            rev_dict = dict((item[1], item[0]) for item in color_d.items())
            genes_temp[random.choice(range(2))] = rev_dict[new_color]
            genes = tuple(genes_temp)
            self.creature.color_genes = genes
        return
        # return genes

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


if __name__ == "__main__":
    c = creatures.Predator()
    m = Mutator(c)
    print c == m.mutate()



