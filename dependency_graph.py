import javalang
import networkx as nx
import matplotlib.pyplot as plt
import os
import json
from utilities import create_directory_if_not_exists

class JavaClassDependencyAnalyzer:
    def __init__(self, target_class):
        self.target_class = target_class
        self.classes = {}
        self.dependencies = nx.DiGraph()

    def analyze(self, code):
        try:
            tree = javalang.parse.parse(code)
            imports = set()
            class_name = None

            # First, collect imports
            for path, node in tree.filter(javalang.tree.Import):
                if isinstance(node, javalang.tree.Import):
                    # Collect imports
                    imports.add(node.path.split(".")[-1])

            # Check if the target class is imported
            if self.target_class in imports:
                # Traverse the tree again to find the class declaration and add dependency
                for path, node in tree:
                    if isinstance(node, javalang.tree.ClassDeclaration):
                        class_name = node.name
                        self.dependencies.add_edge(self.target_class, class_name)
                        self.classes[class_name] = {
                            'name': class_name,
                            'methods': [],
                            'dependencies': set()
                        }
                        break  # We only need to add this class if it imports the target class

            for path, node in tree:
                if isinstance(node, javalang.tree.ClassDeclaration):
                    class_name = node.name
                    self.classes[class_name] = {
                        'name': class_name,
                        'methods': [],
                        'dependencies': set()
                    }

                    # Inheritance (extends)
                    if node.extends:
                        base_class = node.extends.name
                        if base_class == self.target_class:
                            self.dependencies.add_edge(self.target_class, class_name)
                        self.classes[class_name]['dependencies'].add(base_class)
                        self.dependencies.add_edge(class_name, base_class)

                    # Interfaces (implements)
                    if node.implements:
                        for iface in node.implements:
                            iface_name = iface.name
                            if iface_name == self.target_class:
                                self.dependencies.add_edge(self.target_class, class_name)
                            self.classes[class_name]['dependencies'].add(iface_name)
                            self.dependencies.add_edge(class_name, iface_name)

                    # Method calls within the class
                    for method in node.methods:
                        
                        self.classes[class_name]['methods'].append(method.name)
                        if method.body is not None: 
                            for expr in method.body:
                                if isinstance(expr, javalang.tree.MethodInvocation):
                                    called_class = expr.qualifier or ""
                                    self.classes[class_name]['dependencies'].add(called_class)
                                    if called_class == self.target_class:
                                        self.dependencies.add_edge(class_name, called_class)
                    

        except javalang.parser.JavaSyntaxError as e:
            print(f"Syntax error in file: {e}")

    def analyze_project(self, directory):
        # Recursively find all Java files in the project directory
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".java"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                        self.analyze(code)
    
    def export_to_json(self, filename):
        # Create a directed graph
        G = nx.DiGraph()
        # Convert the networkx graph to a dictionary
        graph_data = nx.readwrite.json_graph.node_link_data(self.dependencies)

        # Add nodes to the graph
        for node in graph_data["nodes"]:
            G.add_node(node["id"])
        # Add edges to the graph
        for link in graph_data["links"]:
            G.add_edge(link["source"], link["target"])

        # Verify if the target class exists in the graph
        if self.target_class not in G.nodes:
            print(f"Target class '{self.target_class}' does not exist in the graph.")
            return

        # Get the subgraph for the target class and its connected components
        subgraph_nodes = nx.descendants(G, self.target_class) | {self.target_class}
        self.dependencies = G.subgraph(subgraph_nodes)

        graph_data = nx.readwrite.json_graph.node_link_data(self.dependencies)
        
        # Extract the directory path from the filename
        directory_path = os.path.dirname(filename)
        
        # Create the directory if it does not exist
        if directory_path:
            create_directory_if_not_exists(directory_path)

        # Write the dictionary to a JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=4)


def draw_dependency_graph(graph, filename='java_class_dependency_graph.png'):
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(12, 8))
    nx.draw(graph, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=12, font_weight="bold", arrows=True)
    plt.title("Java Class Dependency Graph")
    plt.savefig(filename)

