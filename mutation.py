"""
This module handles mutation of genes, passing back the mutated gene to the
original caller.
"""

import random
import creatures



class Mutator(object):
    """
    Creates a mutation instance which takes a perticular creature in its
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
        print genes
        print type(genes.items())
        to_mutate = random.choice(genes.items())
        print to_mutate
        new_gene = gene_dict[to_mutate[0]](to_mutate[1])
        print new_gene
        self.creature.__dict__[to_mutate[0]] = new_gene
        print self.creature
        return self.creature



    def mutate_color(self, genes):
        genes_temp = list(genes)
        curr_colors = creatures.Predator.color_dict.values()
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
        # Only transfer the gene if it doesn't exist.
        if new_color not in curr_colors:
            gene_name = "M{0}".format(str(creatures.World.mutation_count))
            creatures.Predator.color_dict[gene_name] = new_color
            creatures.World.mutation_count += 1
            print "MUTATION! Color: {0}".format(new_color)
            genes_temp[1] = gene_name
            genes = tuple(genes_temp)
        return genes

    def mutate_shape(self, genes):
        print "SHAPE MUTATED {0}".format(genes)
        return genes

    def mutate_rotation(self, genes):
        print "ROTATION MUTATED {0}".format(genes)
        return genes

    def mutate_bias(self, genes):
        print "BIAS MUTATED {0}".format(genes)
        return genes

    def mutate_offspringgenes(self, genes):
        print "OFFSPRING GENES MUTATED {0}".format(genes)

        return genes


if __name__ == "__main__":
    c = creatures.Predator()
    m = Mutator(c)
    print c == m.mutate()



