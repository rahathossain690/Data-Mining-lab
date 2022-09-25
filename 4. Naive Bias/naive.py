import numpy as np
import pandas as pd
import sys
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import warnings
warnings.filterwarnings('always')

def getData(dataset_name):
    attribute_file_name = '../Data/'+dataset_name+".attr"
    dataset_file_name = '../Data/'+dataset_name+".data"
    att = pd.read_csv(attribute_file_name,
                      delim_whitespace=True,
                     header = None)
    attributes = {rows[0]:rows[1] for _,rows in att.iterrows()}
    dataset = pd.read_csv(dataset_file_name,
                      names=list(attributes.keys()))
    return attributes, dataset

def getInfo(attributes, dataset):
    Info = {}
    mean = {}
    std = {}
#     grouped = dataset.group_by(dataset['class'])
    for column in dataset.columns:
        if column == 'class' or attributes[column] == 'category': continue
        mean[column] = dataset.groupby('class')[column].mean().to_dict()
        std[column] = dataset.groupby('class')[column].std().to_dict()
    Info['mean'] = mean
    Info['std'] = std
    return Info

def getWinner(attributes, dataset, info, x):
    distinct_class = dataset['class'].value_counts()
    classProb = distinct_class / distinct_class.sum()
    grouped = dataset.groupby(['class'])
    Winner = None
    maxPosterior = -np.inf
    for att_class in distinct_class.index:
        like_hood = 0
        OnlyClassData = grouped.get_group(att_class)
        for column in dataset.columns:
            if column == 'class': continue
            if attributes[column] == 'category':
                grouped_column = (OnlyClassData.groupby(column).count())/len(OnlyClassData)
                if x[column] in grouped_column['class'].index:
                    conditionalProbability = np.log(grouped_column['class'][x[column]])
                else: 
                    conditionalProbability = np.log(1e-6)
                like_hood += conditionalProbability
            else:
                conditionalProbability = getNPDF(x[column], info['mean'][column][att_class], info['std'][column][att_class])
                conditionalProbability += 1e-6
                like_hood += np.log(conditionalProbability)
        posterior = like_hood+np.log(classProb[att_class])
        if posterior > maxPosterior: 
            maxPosterior = posterior
            Winner = att_class
    if Winner == None: 
        print(x)
    return Winner

def getNPDF(val, mu, sigma):
    sigma = sigma if sigma != 0 else self.eps 
    exponentTerm = (-1) * ( ( (val-mu) ** 2 ) / ( 2 * (sigma ** 2) ) )
    return (1/(np.sqrt(2*np.pi) * sigma)) * np.exp(exponentTerm)

def predict(attributes, dataset, XTest):
    info = getInfo(attributes, dataset)
    YPred = []
    for index,row in XTest.iterrows():
        YPred.append( getWinner(attributes, dataset, info, row) )
    return np.array(YPred)

def statistics(Y,YPred):
    accuracy = accuracy_score(Y, YPred)*100
    precision = precision_score(Y, YPred, average="macro")*100
    recall = recall_score(Y, YPred, average="macro")*100
    f1 = f1_score(Y, YPred, average="macro")*100
    return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}

attr, data = getData(str(sys.argv[1]))

training_data, testing_data = train_test_split(data, test_size = float(sys.argv[2]))
yTest = predict(attr, training_data, testing_data)
stat = statistics(list(testing_data['class']), yTest)
print( stat )