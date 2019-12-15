from .models import *

class PuzzleNode:
    ''' Wrapper class around a puzzle with parent and child pointers. '''

    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.parents = []
        self.canonical_parent = None
        self.children = []

    def __str__(self):
        def __root_str(node):
            return node.puzzle.__str__() if node.puzzle else "ROOT"
        root_puzzle = __root_str(self)
        parents_str = ",".join([__root_str(node) for node in self.parents])
        children_str = ",".join([__root_str(node) for node in self.children])
        return "root: %s\nparents: %s\nchildren: %s" % (root_puzzle, parents_str, children_str)

    def get_sorted_nodes(self):
        output = [self]
        def __sortkey(node):
            '''
            Unsolved children should come before SOLVED children.
            After that, childless should come first.
            '''
            return (node.puzzle.status == Puzzle.SOLVED, len(node.children) > 0)

        for child in sorted(self.children, key=__sortkey):
            output.extend(child.get_sorted_nodes())

        return output


class PuzzleTree:
    '''
    Tree representation of a set of puzzles. Each node is represented by a puzzle.
    A node is a parent node of another node if the former is a metapuzzle for the latter.
    Note that this is not *really* a tree since we allow nodes to have multiple parents in
    order to support multiple metas per puzzle.
    '''

    def __init__(self, puzzles):
        ''' Initialize tree. It is assumed that puzzles contains unique puzzles (no dups). '''
        # A fake node to contain all the metaless puzzles as children.
        self.root = PuzzleNode(None)
        # Construct nodes for each puzzle
        # Dictionary mapping puzzle PK -> list of nodes
        self.puzzle_to_node = {p.pk : PuzzleNode(p) for p in puzzles}

        # Construct parent/child edges
        for p in puzzles:
            node = self.puzzle_to_node[p.pk]
            if not p.has_assigned_meta():
                self.root.children.append(node) # This also adds node to node.children for ALL nodes for some reason
                node.parents = [self.root]
            else:
                node.parents = [self.puzzle_to_node[meta.pk] for meta in p.metas.all()]
                for parent_node in node.parents:
                    parent_node.children.append(node) # This adds node to node.children for some reason
        

    def get_sorted_nodes(self):
        '''
        Returns a list of PuzzleNodes representing the ordering in which the puzzles should be
        displayed in the table. Note that because of multiple parent support, some nodes may be
        duplicated in the list.
        '''
        return self.root.get_sorted_nodes()[1:]
