import math


class Node:
    def __init__(self, name, parent=None, support=0, next=None):
        self.name = name
        self.parent = parent
        self.support = support
        self.next = next
        self.children = dict()
    
    def get_child(self, child_name, default_value=None):
        return self.children.get(child_name, default_value)
    
    def add_child(self, node):
        self.children[ node.name ] = node
    
    def remove_child(self, node)
        del self.children[node]
    
    def print(self):
        print("name = {0} parent = {1} support = {2} next = {3}".format(self.name, self.parent.name if self.parent is not None else "None", self.support, self.next.name if self.next is not None else "None"))
        for child in self.children.values():
            child.print()

def borrow_new_node(node_storage, f_name):
    node = node_storage[f_name]
    if node is None:
        node = Node(name=f_name, support=0, parent=None, next=None)
        node_storage[f_name] = node
        return node
    while node.next is not None:
        node = node.next
    node.next = Node(name=f_name, support=0, parent=None, next=None)
    return node.next

    

def generate_fp_transection(root, transection, current_index, node_storage):
    if current_index == len(transection):
        return
    if root.children.get_child(transection[current_index]) == None:
        node = borrow_new_node(node_storage, transection[current_index])
        node.parent = root
    root.get_child(transection[current_index]).support += 1
    generate_fp_transection(root.get_child(transection[current_index]), transection, current_index + 1, node_storage)

def build_fp_tree(root, transections, node_storage):
    for transection in transections:
        generate_fp_transection(root, transection, 0, node_storage)

def get_node_storage(initial_count):
    return {key: None for key in initial_count.keys()}

def get_initial_count(transections, min_support):
    counter = dict()
    for transection in transections:
        for item in transection:
            counter[item] = counter.get(item, 0) + 1
    to_delete = [key for key, value in counter.items() if value < min_support]
    for key in to_delete:
        del counter[key]
    return {key: value for key, value in sorted(counter.items(), key=lambda item: -item[1]) }

def mock_data():
    return [
        ['a', 'b'],
        ['b', 'c', 'd'],
        ['a', 'c', 'd', 'e'],
        ['a', 'd', 'e'],
        ['a', 'b', 'c'],
        ['a', 'b', 'c', 'd'],
        ['a', 'f'],
        ['a', 'b', 'c'],
        ['a', 'd', 'b'],
        ['b', 'c', 'e']
    ]

def get_rearranged_transection(transections, initial_count):
    new_transections = list()
    for transection in transections:
        new_transection = list()
        for item in initial_count.keys():
            if item in transection:
                new_transection.append(item)
        new_transections.append(new_transection)
    return new_transections


def fp_growth(transections, min_support_perc):
    min_support = math.ceil(len(transections) * min_support_perc)
    initial_count = get_initial_count(transections, min_support)
    node_storage = get_node_storage(initial_count)
    rearranged_transections = get_rearranged_transection(transections, initial_count)
    root = Node(name="root", support=0)
    build_fp_tree(root, rearranged_transections, node_storage)
    root.print()
    

def main():
    data = mock_data()
    min_support = 0.3
    frequent_patterns = fp_growth(data, min_support)



if __name__ == "__main__":
    main()