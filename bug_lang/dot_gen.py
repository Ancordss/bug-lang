import pydot

class DotGenerator:
    def __init__(self):
        self.graph = pydot.Dot(graph_type='digraph')

    def generate(self, node, parent_id=None):
        node_id = str(id(node))
        node_label = type(node).__name__

        self.graph.add_node(pydot.Node(node_id, label=node_label))

        if parent_id:
            self.graph.add_edge(pydot.Edge(parent_id, node_id))

        for child_name, child in self.get_children(node):
            if isinstance(child, list):
                for item in child:
                    self.generate(item, node_id)
            elif hasattr(child, '__dict__'):
                self.generate(child, node_id)

    def get_children(self, node):
        if hasattr(node, '__dict__'):
            return node.__dict__.items()
        else:
            return []

    def to_dot(self):
        return self.graph.to_string()
