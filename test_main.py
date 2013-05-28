import unittest
import sys

sys.path.append('/Users/cqoverly/Darwin/')
from main import Predator, World, Mutator, ControlPanel, Container, DarwinApp

class PredatorTestCase(unittest.TestCase):

    def setUp(self):
        self.root = Widget()
        self.cls = Predator


    def test_add_Predator(self):

        root = self.root
        self.assertEqual(root.children, [])
        c1 = self.cls()
        root.add_widget(c1)
        self.assertEqual(root.children, [c1])
        root.remove_widget(c1)
        self.assertEqual(root.children, [])

    def test_color_name(self):
        pred = Predator()
        self.assertEqual(self.color_name, 'b' )

    def test_area(self):
        pred = Predator()
        pred.gender = 'F'
        self.assertEqual(self.area, 4)

    def test_shape(self):
        pred = Predator()
        self.assertEqual(pred.shape, 'Rectangle')