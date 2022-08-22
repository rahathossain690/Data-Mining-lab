
##                  
##   Rahat Hossain  
##     9-8-2022     
#
# 1. Put the dataset in the same folder
# 2. open terminal and write "python3 apriori.py dataset.txt 0.8"  
#     here dataset.txt is the dataset and 0.8 is the minimum support count
#     other formats are also supported
# 3. The result will be shown accordingly
#
##
##
##


import sys, os, psutil, timeit, math

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
    ], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


class Node:
    def __init__(self, name, support=0, parent=None, next=None):
        self.name = name
        self.support = support
        self.parent = parent
        self.next = next
        self.children = dict()
    
    def get_child(self, name, default_return=None):
        return self.children.get(name, default_return)
    
    def add_child(self, node):
        self.children[node.name] = node
    
    def remove_child(self, name):
        del self.children[name]
    
    def print(self):
        print("name = {0} parent = {1} support = {2} next = {3}".format(self.name, self.parent.name if self.parent is not None else "None", self.support, self.next.name if self.next is not None else "None"))
        for child in self.children.values():
            child.print()


def create_tree(transections, frequency, min_support):
    item_set = dict()
    for idx, transection in enumerate(transections):
        for item in transection:
            item_set[item] = item_set.get(item, 0) + frequency[idx]
    frequent_items = dict()
    for key,value in item_set.items():
        if value >= min_support:
            frequent_items[key] = value
    del item_set
    header_table = dict()
    for key,value in frequent_items.items():
        header_table[key] = [value, None]
    del(frequent_items)
    root = Node(name="root")
    for idx, transection in enumerate(transections):
        transection = list(filter(lambda v: v in header_table, transection))
        transection.sort(key=lambda item: header_table[item][0], reverse=True)
        current_node = root
        for item in transection:
            current_node = update_tree(item, current_node, header_table, frequency[idx])
    return root, header_table

def update_tree(item, root, header_table, frequency):
    if root.get_child(item) is not None:
        root.get_child(item).support += frequency
    else:
        node = Node(name=item, support=frequency, parent=root)
        root.add_child(node)
        update_header(item, node, header_table)
    return root.get_child(item)

def update_header(item, node, header_table):
    if header_table[item][1] is None:
        header_table[item][1] = node
    else:
        temp_node = header_table[item][1]
        while temp_node.next is not None:
            temp_node = temp_node.next
        temp_node.next = node


def mine_tree(header_table, min_support, prefix, frequent_patterns):
    for key, value in header_table.items():
        pattern = ""
        if prefix == "":
            pattern = prefix + str(key)
        else:
            pattern = prefix + "," + str(key)
        frequent_patterns[pattern] = frequent_patterns.get(pattern, 0) + value[0]
        conditional_pattern_base, frequency = get_conditional_pattern_base(key, header_table)
        conditional_tree, new_header_table = create_tree(conditional_pattern_base, frequency, min_support)
        if new_header_table is not None:
            mine_tree(new_header_table, min_support, pattern, frequent_patterns)

def get_conditional_pattern_base(key, header_table):
    node = header_table[key][1]
    conditional_patterns = list()
    frequency = list()
    if node is not None:
        prefix_path = list()
        go_down_tree(node, prefix_path)
        if len(prefix_path) > 1:
            conditional_patterns.append(prefix_path[1:])
            frequency.append(node.support)
        node = node.next
    return conditional_patterns, frequency

def go_down_tree(node, prefix_path):
    if node.parent is not None:
        prefix_path.append(node.name)
        go_down_tree(node.parent, prefix_path)


def fp_growth(transections, frequency, min_support_perc):
    min_support = math.ceil(len(transections) * min_support_perc)
    root, header_table = create_tree(transections, frequency, min_support) 
    del transections
    frequent_patterns = dict()
    mine_tree(header_table, min_support, "", frequent_patterns)
    return frequent_patterns

def get_transections(filename):
    data = list()
    frequency = list()
    with open(filename, "r", encoding="utf-8") as file:
        for line in file.readlines():
            row = line.strip().split()
            row = [int(item) for item in row]
            row.sort()
            data.append(row)
            frequency.append(1)
    return data, frequency

def get_process_memory():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss

def main():
    filename, min_support_perc = str(sys.argv[1]), float(sys.argv[2])


    start_time = timeit.default_timer()
    mem_before = get_process_memory()

    transections, frequency = get_transections(filename)
    
    frequent_patterns = fp_growth(transections, frequency, min_support_perc)

    end_time = timeit.default_timer()
    mem_after = get_process_memory()

    print(" ")
    print("Time taken:", end_time - start_time, "Memory taken:", mem_after - mem_before)

    print("\nTotal patterns:", len(frequent_patterns))
    print(frequent_patterns)


if __name__ == "__main__":
    main()