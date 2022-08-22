
##                  
##   Rahat Hossain  
##     9-8-2022     
#
# 1. Put the dataset in the same folder
# 2. open terminal and write "python3 fp_growth.py {{../Data/dataset.txt}} {{minimum_support_percentage}}"  
#     here dataset.txt is the dataset and 0.8 is the minimum support count
#     other formats are also supported
# 3. The result will be shown accordingly
#
##
##
##

import sys, os, psutil, timeit, math

total_join, total_prune = 0, 0

def mock_transections():
    # used for testing purpose
    return [
        ["A", "B"],
        ["A", "B", "C"],
        ["B"],
        ["B", "C"],
        ["A", "D"],
        ["A", "D"],
        ["C", "D"]
    ]


class Node:
    def __init__(self, name='root', counter=0):
        self.name = name
        self.counter = counter
        self.children = dict()
    
    def is_end(self):
        return len(self.children) == 0
    
    def add_child(self, node):
        self.children[ node.name ] = node

    def print(self, depth=0): # for testing purpose
        return_str = ""
        return_str += ("  " * depth)
        return_str += "Node name = '" + str(self.name) + "' counter = " + str(self.counter) + " with children size = " + str( len(self.children) )
        print(return_str)
        for _, child in self.children.items():
            child.print(depth + 1)


def first_insert(root, item_count, minimum_count):
    for item in sorted(item_count):
        if item_count[item] < minimum_count:
            global total_prune
            total_prune += 1
            continue
        node = Node(name=item, counter=item_count[item])
        root.add_child(node)
    
def find_candidate(root):
    if root.is_end():
        return
    keys = list(root.children.keys())
    for i in range( len(keys)  ):
        current_node = root.children[ keys[i] ]
        if current_node.is_end():
            for j in range(i + 1, len(keys) ):
                node = Node(root.children[ keys[j] ].name)
                current_node.add_child(node)
                global total_join
                total_join += 1
        else:
            find_candidate(current_node)

def frequency_count(root, transection, left=0): 
    if root.is_end():
        root.counter += 1
        return
    for child in root.children.values():
        if child.name in transection[left:]:
            offset = transection[left:].index(child.name)
            frequency_count(child, transection, offset + left)

def database_scan(root, transections):
    for transection in transections:
        frequency_count(root, transection)

def remove_non_frequent_element(root, minimum_count, level, current_level):
    if root.is_end():
        if current_level < level or root.counter < minimum_count: 
            return True
        return False
    deleted_key = [key for key, value in root.children.items() if remove_non_frequent_element(value, minimum_count, level, current_level + 1)]
    for key in deleted_key:
        del root.children[key]
        global total_prune
        total_prune += 1
    return len(root.children) == 0

def get_frequent_candidates(root, candidates, support_count):
    if root.is_end():
        if root.name != "root":
            support_count[candidates] = root.counter
        return
    if len(candidates) != 0:
        candidates += ","
    for child in root.children.values():
        get_frequent_candidates(child, candidates + str(child.name), support_count)


def get_item_count(transections):
    item_count = dict()
    for transection in transections:
        for item in transection:
            item_count[ item ] = item_count.get(item, 0) + 1
    return item_count

def apriori(transections, minimum_support):
    item_count = get_item_count(transections)
    minimum_count = math.ceil( len(transections) * minimum_support )
    root = Node()
    level_no = 1
    frequent_patterns = dict()
    level_prune, level_join, level_candidates = 0, 0, 0
    while True:
        if level_no == 1:
            first_insert(root=root, item_count=item_count, minimum_count=minimum_count)
        else:
            find_candidate(root=root)
            database_scan(root, transections)
            remove_non_frequent_element(root, minimum_count, level_no, 0)
        if root.is_end():
            break
        get_frequent_candidates(root, "", frequent_patterns)
        global total_join, total_prune
        print("Level =", level_no, "Join =", total_join - level_join, "Prune =", total_prune - level_prune, "Candidates =", len(frequent_patterns) - level_candidates)
        level_join = total_join
        level_prune = total_prune
        level_candidates = len(frequent_patterns)
        level_no += 1
    return frequent_patterns


def get_transections(filename):
    data = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file.readlines():
            row = line.strip().split()
            row = [int(item) for item in row]
            row.sort()
            data.append(row)
    return data

def get_process_memory():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss

def main():
    filename, minimum_support = str(sys.argv[1]), float(sys.argv[2])

    start_time = timeit.default_timer()
    mem_before = get_process_memory()

    transections = get_transections(filename)
    frequent_patterns = apriori(transections, minimum_support)

    end_time = timeit.default_timer()
    mem_after = get_process_memory()

    print(" ")
    print("Time taken:", end_time - start_time, "Memory taken:", mem_after - mem_before)

    print("\nTotal patterns:", len(frequent_patterns))
    print("Pattern ( pattern_count ):")
    for pattern, pattern_count in frequent_patterns.items():
        print(pattern, "(", pattern_count, ")")


if __name__ == '__main__':
    main()