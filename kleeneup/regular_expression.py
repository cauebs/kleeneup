from lark.tree import pydot__tree_to_png    # Just a neat utility function
from lark import Lark, Tree
from lark.lexer import Token
from enum import Enum, auto
from finite_automaton import FiniteAutomaton, State, Symbol

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
                 %import common.DIGIT
                 %import common.WS
                 %ignore WS

                 SYMBOL: DIGIT | LCASE_LETTER
    ''', start='e')


class Lambda:
    pass


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
        self.visited_up = False
        self.visited_down = False

    @classmethod
    def from_lark_tree(cls, l_tree):
        if type(l_tree) is Tree:
            try:
                left = cls.from_lark_tree(l_tree.children[0])
            except AttributeError:
                left = StitchedBinaryTree(
                    Operation[l_tree.children[0].value.upper()])
            except IndexError:
                left = None

            try:
                right = cls.from_lark_tree(l_tree.children[1])
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
        inorder = list(self.inorder())

        for i in range(0, len(inorder)):
            current = inorder[i]
            if (current.data != Operation['UNION'] and
                    current.data != Operation['CONCATENATION']):
                try:
                    current.seam = inorder[i+1]
                except IndexError:
                    current.seam = Lambda

    def reachable_symbols(
        self,
        direction,
        reachable=None,
        visited_down=None,
        visited_up=None
    ):
        if reachable is None:
            reachable = set()

        if visited_down is None:
            visited_down = set()

        if visited_up is None:
            visited_up = set()

        if direction == 'DOWN':
            if self not in visited_down:
                visited_down.add(self)
                if self.data == Operation['UNION']:
                    self.left.reachable_symbols(
                        'DOWN', reachable=reachable, visited_down=visited_down, visited_up=visited_up)
                    self.right.reachable_symbols(
                        'DOWN', reachable=reachable, visited_down=visited_down, visited_up=visited_up)

                elif self.data == Operation['CONCATENATION']:
                    self.left.reachable_symbols(
                        'DOWN', reachable=reachable, visited_down=visited_down, visited_up=visited_up)

                elif self.data == Operation['OPTION']:
                    self.left.reachable_symbols(
                        'DOWN', reachable=reachable, visited_down=visited_down, visited_up=visited_up)
                    try:
                        self.seam.reachable_symbols(
                            'UP', reachable=reachable, visited_down=visited_down, visited_up=visited_up)
                    except AttributeError:
                        reachable.add(Lambda)

                elif self.data == Operation['KLEENESTAR']:
                    self.left.reachable_symbols(
                        'DOWN', reachable=reachable, visited_down=visited_down, visited_up=visited_up)
                    try:
                        self.seam.reachable_symbols(
                            'UP', reachable=reachable, visited_down=visited_down, visited_up=visited_up)
                    except AttributeError:
                        reachable.add(Lambda)

                else:
                    reachable.add(self)

        elif direction == 'UP':
            if self not in visited_up:
                visited_up.add(self)
                if self.data == Operation['UNION']:
                    rightmost = self.right
                    while True:
                        if rightmost.right:
                            rightmost = rightmost.right
                        else:
                            break
                    rightmost.seam.reachable_symbols(
                        'UP', reachable=reachable, visited_down=visited_down, visited_up=visited_up)

                elif self.data == Operation['CONCATENATION']:
                    self.right.reachable_symbols(
                        'DOWN', reachable=reachable, visited_down=visited_down, visited_up=visited_up)

                elif self.data == Operation['OPTION']:
                    try:
                        self.seam.reachable_symbols(
                            'UP', reachable=reachable, visited_down=visited_down, visited_up=visited_up)
                    except AttributeError:
                        reachable.add(Lambda)

                elif self.data == Operation['KLEENESTAR']:
                    self.left.reachable_symbols(
                        'DOWN', reachable=reachable, visited_down=visited_down, visited_up=visited_up)
                    try:
                        self.seam.reachable_symbols(
                            'UP', reachable=reachable, visited_down=visited_down, visited_up=visited_up)
                    except AttributeError:
                        reachable.add(Lambda)

                else:
                    try:
                        self.seam.reachable_symbols(
                            'UP', reachable=reachable, visited_down=visited_down, visited_up=visited_up)
                    except AttributeError:
                        reachable.add(Lambda)

        return reachable

    def inorder(self):
        if self.left:
            for x in self.left.inorder():
                yield x

        yield self

        if self.right:
            for x in self.right.inorder():
                yield x

    def __str__(self):
        return f"{self.data}"

    def __repr__(self):
        return f"<StitchedBinaryTree '{self.__str__()}'>"


class RegularExpression:
    def __init__(self, string):
        self.expression = string

    def to_regular_automaton(self):
        d_tree = parser.parse(self.expression)
        s_tree = StitchedBinaryTree.from_lark_tree(d_tree)
        s_tree.sew()

        symbols = set()
        for node in s_tree.inorder():
            if type(node.data) is str:
                symbols.add(Symbol(node.data))

        # De Simone's algorithm
        initial_state = State('Q0')
        transitions = {}
        initial_composition = frozenset(s_tree.reachable_symbols('DOWN'))

        compositions = {
            initial_composition: initial_state
        }

        if Lambda in initial_composition:
            accept_states = set([initial_state])
        else:
            accept_states = set()

        unvisited_compositions = [initial_composition]

        state_index = 1
        while True:
            try:
                current_comp = unvisited_compositions.pop(0)
            except IndexError:
                break

            for s in symbols:
                new_comp = set()
                for node in current_comp:
                    try:
                        if node.data == s.value:
                            new_comp = new_comp.union(
                                node.reachable_symbols('UP'))
                    except AttributeError:
                        pass

                new_comp = frozenset(new_comp)
                if len(new_comp) > 0:
                    if new_comp not in compositions:
                        unvisited_compositions.append(new_comp)
                        new_state = State(f"Q{state_index}")
                        compositions[new_comp] = new_state

                        transitions[(compositions[current_comp], s)
                                    ] = new_state
                        if Lambda in new_comp:
                            accept_states.add(new_state)

                        state_index += 1
                    else:
                        transitions[(compositions[current_comp], s)
                                    ] = compositions[new_comp]

        return FiniteAutomaton(transitions, initial_state, accept_states)
