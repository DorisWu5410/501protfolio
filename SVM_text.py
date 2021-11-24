#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 03:05:07 2021

@author: jiahuiwu
"""

import pandas as pd


data1_2 = pd.read_csv('/Users/jiahuiwu/Desktop/501/portfolio/DT_text.csv')



from sklearn import model_selection, naive_bayes, svm


Train_X, Test_X, Train_Y, Test_Y = model_selection.train_test_split(data1_2.iloc[:,1:200],data1_2['lable'],test_size=0.3)

# fit the training dataset on the NB classifier
Naive = naive_bayes.MultinomialNB()
Naive.fit(Train_X,Train_Y)
# predict the labels on validation dataset
predictions_NB = Naive.predict(Test_X)
pd.crosstab(Test_Y, pd.Series(predictions_NB), rownames=['Actual'], colnames=['Predicted'], margins = True)

# Classifier - Algorithm - SVM
# fit the training dataset on the classifier
SVM = svm.SVC(C=1.0, kernel='linear', degree=3, gamma='auto')
SVM.fit(Train_X,Train_Y)
# predict the labels on validation dataset
predictions_SVM = SVM.predict(Test_X)
pd.crosstab(Test_Y, pd.Series(predictions_SVM), rownames=['Actual'], colnames=['Predicted'], margins = True)

SVM2 = svm.SVC(C=1.0, kernel='poly', degree=3, gamma='auto')
SVM2.fit(Train_X,Train_Y)
# predict the labels on validation dataset
predictions_SVM2 = SVM2.predict(Test_X)
pd.crosstab(Test_Y, pd.Series(predictions_SVM2), rownames=['Actual'], colnames=['Predicted'], margins = True)

SVM3 = svm.SVC(C=1.0, kernel='sigmoid', degree=3, gamma='auto')
SVM3.fit(Train_X,Train_Y)
# predict the labels on validation dataset
predictions_SVM3 = SVM3.predict(Test_X)
pd.crosstab(Test_Y, pd.Series(predictions_SVM3), rownames=['Actual'], colnames=['Predicted'], margins = True)

from sklearn.metrics import accuracy_score

print("Naive Bayes Accuracy Score -> ",accuracy_score(predictions_NB, Test_Y)*100)
print("SVM Accuracy Score -> ",accuracy_score(predictions_SVM, Test_Y)*100)










