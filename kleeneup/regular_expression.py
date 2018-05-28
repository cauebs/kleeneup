from lark.tree import pydot__tree_to_png    # Just a neat utility function
from lark import Lark, Tree
from lark.lexer import Token
from enum import Enum, auto

parser = Lark('''?e: e "|" a -> union
                   | a

                 ?a: a "." b -> concatenation
                   | b

                 ?b: b "*" -> kleenestar
                   | c

                 ?c: c "?" -> option
                   | d

                 ?d: "(" e ")"
                   | SYMBOL

                 %import common.LCASE_LETTER
                 %import common.SIGNED_NUMBER
                 %import common.WS
                 %ignore WS

                 SYMBOL: SIGNED_NUMBER | LCASE_LETTER
    ''', start='e')


class Operation(Enum):
    UNION = auto()
    CONCATENATION = auto()
    KLEENESTAR = auto()
    OPTION = auto()


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
                left = StitchedBinaryTree(
                    Operation[l_tree.children[0].value.upper()])
            except IndexError:
                left = None

            try:
                right = self.from_lark_tree(l_tree.children[1])
            except AttributeError:
                right = StitchedBinaryTree(
                    Operation[l_tree.children[1].value.upper()])
            except IndexError:
                right = None

            return StitchedBinaryTree(
                Operation[l_tree.data.upper()],
                left,
                right
            )

        else:
            return StitchedBinaryTree(l_tree.value)

    def sew(self):
        inorder = self.inorder()

        for i in range(0, len(inorder)):
            current = inorder[i]
            if (current.data != Operation['UNION'] and
                    current.data != Operation['CONCATENATION']):
                try:
                    current.seam = inorder[i+1]
                except IndexError:
                    current.seam = 'LAMBDA'

    def reachable_symbols(self, direction):
        '''Just prints the reachable symbols for now'''
        if direction == 'DOWN':
            if self.data == Operation['UNION']:
                self.left.reachable_symbols('DOWN')
                self.right.reachable_symbols('DOWN')

            elif self.data == Operation['CONCATENATION']:
                self.left.reachable_symbols('DOWN')

            elif self.data == Operation['OPTION']:
                self.left.reachable_symbols('DOWN')
                try:
                    self.seam.reachable_symbols('UP')
                except AttributeError:
                    print('LAMBDA')

            elif self.data == Operation['KLEENESTAR']:
                self.left.reachable_symbols('DOWN')
                try:
                    self.seam.reachable_symbols('UP')
                except AttributeError:
                    print('LAMBDA')

            else:
                print(self)

        elif direction == 'UP':
            if self.data == Operation['UNION']:
                rightmost = self.right
                while True:
                    if rightmost.right:
                        rightmost = rightmost.right
                    else:
                        break
                rightmost.seam.reachable_symbols('UP')

            elif self.data == Operation['CONCATENATION']:
                self.right.reachable_symbols('DOWN')

            elif self.data == Operation['OPTION']:
                try:
                    self.seam.reachable_symbols('UP')
                except AttributeError:
                    print('LAMBDA')

            elif self.data == Operation['KLEENESTAR']:
                self.left.reachable_symbols('DOWN')
                try:
                    self.seam.reachable_symbols('UP')
                except AttributeError:
                    print('LAMBDA')

            else:
                try:
                    self.seam.reachable_symbols('UP')
                except AttributeError:
                    print('LAMBDA')

    def is_leaf(self):
        return not (self.left or self.right)

    def inorder(self):
        stack = []
        inorder = []

        current = self
        while True:
            if current:
                stack.append(current)
                current = current.left

            else:
                if len(stack) > 0:
                    current = stack.pop()
                    inorder.append(current)

                    current = current.right

                else:
                    break

        return inorder

    def traversal_inorder(self):
        if self.left:
            for x in self.left.traversal_inorder():
                yield x

        yield self.data

        if self.right:
            for x in self.right.traversal_inorder():
                yield x

    def __str__(self):
        return f"{self.data}"


class RegularExpression:
    def __init__(self, string):
        self.expression = string

    @classmethod
    def to_regular_automaton(self):
        lark_tree = parser.parse(self.expression)


tree = parser.parse('a*.(b?.c|d)*')
# tree = parser.parse('a**')
st = StitchedBinaryTree.from_lark_tree(tree)
st.sew()
st.reachable_symbols('DOWN')
