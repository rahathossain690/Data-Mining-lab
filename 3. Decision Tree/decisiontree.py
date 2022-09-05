###
# @ Rahat Hossain
# 4 Sept, 2022
###

import pandas as pd
import numpy as np
import math


filename, attributes, dataset = None, None, None

def main():
    test_size = 0.2
    from sklearn.model_selection import train_test_split
    training_data, testing_data = train_test_split(dataset, test_size=test_size)
    features = training_data.columns
    features = features[features!= 'class']

    tree = create_decision_tree(training_data,features)
    accuracy, precision, recall, f1 = test(testing_data,tree, features)
    print('dataset\t=\t' + filename + '\ntest size\t=\t'+str(test_size)+"\naccuracy\t=\t"+str(accuracy)+"\nprecision\t=\t"+str(precision)+"\nrecall\t=\t"+str(recall)+"\nf1\t=\t"+str(f1))


def get_entropy(target_col, col_type, split_point=0.0):
    if col_type == 'category':
        counts = list(target_col.value_counts().values)
    else:
        left = target_col <= split_point
        right = target_col > split_point
        counts = [len(target_col[left]), len(target_col[right])]
    entropy = np.sum([(-counts[i]/np.sum(counts))*np.log2(counts[i]/np.sum(counts)) for i in range(len(counts))])
    return entropy

def get_info_gain(data,split_attribute_name,split_att_type,target_name="class"):
    total_entropy = get_entropy(data[target_name], attributes[target_name])
    values = list(np.unique(data[split_attribute_name]))
    best = 0
    idx = None
    for val in values:
        left = data[split_attribute_name] <= val
        right = data[split_attribute_name] > val
        counts = [len(data[split_attribute_name][left]), len(data[split_attribute_name][right])]
        Weighted_Entropy = (counts[0]/np.sum(counts))*get_entropy(data.where(data[split_attribute_name]<=val).dropna()[target_name], attributes[target_name], val) + (counts[1]/np.sum(counts))*get_entropy(data.where(data[split_attribute_name]>val).dropna()[target_name], attributes[target_name], val)
        Information_Gain = total_entropy - Weighted_Entropy
        if Information_Gain == 0.0:
            continue
        Gain_Ratio = Information_Gain/get_entropy(data[split_attribute_name], attributes[split_attribute_name], val)
        if Gain_Ratio>=best:
            best = Gain_Ratio
            idx = val
    return best, idx

def create_decision_tree(data,features,target_attribute_name="class",parent_node_class = None):
    if len(features)==0 or len(data) == 0:
        return parent_node_class
    try:
        if len(np.unique(data[target_attribute_name])) <= 1:
            return np.unique(data[target_attribute_name])[0]
    except KeyError:
        print("Key Error")
    else:
        parent_node_class = data[target_attribute_name].value_counts().idxmax()
        max_GR = -np.inf 
        for feature in features:
            GR, point = get_info_gain(data,feature,target_attribute_name)
            if GR> max_GR:
                max_GR = GR
                split_point = point
                best_feature = feature
        tree = {best_feature:{}}
        features = features[features != best_feature]
        if attributes[best_feature] == 'category':
            grouped = data.groupby(data[best_feature])
            for value in np.unique(data[best_feature]):
                sub_data = grouped.get_group(value)
                if best_feature != target_attribute_name:
                    del sub_data[best_feature]
                subtree = create_decision_tree(sub_data,features,target_attribute_name,parent_node_class)
                tree[best_feature][value] = subtree
            return(tree)
        else:
            sub_data1 = data[data[best_feature]<=split_point]
            sub_data2 = data[data[best_feature]>split_point]
            if best_feature != target_attribute_name:
                del sub_data1[best_feature]
                del sub_data2[best_feature]
            subtree1 = create_decision_tree(sub_data1,features,target_attribute_name,parent_node_class)
            subtree2 = create_decision_tree(sub_data2,features,target_attribute_name,parent_node_class)
            tree[best_feature][split_point] = [subtree1, subtree2]
            return(tree)

def predict(query,tree,default = 1):
    if not isinstance(tree, dict):
        return tree
    att_name = list(tree.keys())[0]
    if attributes[att_name] == 'category':
        try:
            result_tree = tree[att_name][query[att_name]]
        except:
            return default
        result_tree = tree[att_name][query[att_name]]
        return predict(query, result_tree)
    else:
        key_val = list(tree[att_name].keys())[0]
        if  query[att_name]<=key_val:
            result_tree = tree[att_name][key_val][0]
        else:
            result_tree = tree[att_name][key_val][1]
        return predict(query, result_tree)


def test(data,tree, features):
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    original_data = list(data['class'])
    queries = data[features].to_dict(orient = "records")
    predictions = [predict(query,tree) for query in queries]
    accuracy = accuracy_score(original_data, predictions)
    precision = precision_score(original_data, predictions, average="macro")
    recall = recall_score(original_data, predictions, average="macro")
    f1 = f1_score(original_data, predictions, average="macro")
    return accuracy*100, precision*100, recall*100, f1*100

def get_data(filename):
    attribute_file = filename + '.attr'
    data_file = filename + '.val'
    att = pd.read_csv(attribute_file,
                      delim_whitespace=True,
                     header = None)
    # print(att)
    attributes = {rows[0]:rows[1] for _,rows in att.iterrows()}
    dataset = pd.read_csv(data_file,
                      names=list(attributes.keys()))
    dataset = dataset.dropna()
    return attributes, dataset

if __name__ == "__main__":
    import sys
    filename = str(sys.argv[1])
    attributes, dataset = get_data(filename)
    main()