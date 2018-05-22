from lark.tree import pydot__tree_to_png    # Just a neat utility function
from lark import Lark, Tree
from lark.lexer import Token

parser = Lark('''?e: e "|" a -> union
                   | a

                 ?a: a "." b -> concatenation
                   | b

                 ?b: c "*" -> kleenestar
                   | c

                 ?c: d "?" -> optional
                   | d

                 ?d: "(" e ")"
                   | SYMBOL

                 %import common.LCASE_LETTER
                 %import common.SIGNED_NUMBER
                 %import common.WS
                 %ignore WS

                 SYMBOL: SIGNED_NUMBER | LCASE_LETTER
    ''', start='e')

tree = parser.parse('a*.(b?.c|d)*')


class StitchedBinaryTree:
    def __init__(self, data, left=None, right=None, seam=None):
        self.data = data
        self.left = left
        self.right = right
        self.seam = seam

    @classmethod
    def from_lark_tree(self, l_tree):
        if type(l_tree) is Tree:
            try:
                left = self.from_lark_tree(l_tree.children[0])
            except AttributeError:
                left = StitchedBinaryTree(l_tree.children[0].value)
            except IndexError:
                left = None

            try:
                right = self.from_lark_tree(l_tree.children[1])
            except AttributeError:
                right = StitchedBinaryTree(l_tree.children[1].value)
            except IndexError:
                right = None

            return StitchedBinaryTree(l_tree.data, left, right)

        else:
            return StitchedBinaryTree(l_tree.value)

    def sew(self):
        ...

    def reachable(self, start_node):
        ...

    def traversal_inorder(self):
        if self.left:
            for x in self.left.traversal_inorder():
                yield x

        yield self.data

        if self.right:
            for x in self.right.traversal_inorder():
                yield x


class RegularExpression:
    def __init__(self, string):
        self.expression = string

    @classmethod
    def to_regular_automaton(self):
        lark_tree = parser.parse(self.expression)
