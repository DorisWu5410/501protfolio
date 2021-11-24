train = read.csv('train.csv')
test =  read.csv('test.csv')


SVM1 = svm.SVC(C=1.0, max_iter=20000)
SVM1.fit(train.iloc[idx1,[0,1,2,3,5,6]], train['label'].iloc[idx1])
SVMpred1 = SVM1.predict(test.iloc[:,[0,1,2,3,5,6]])
pd.crosstab(test['label'], pd.Series(SVMpred1), rownames=['Actual'], colnames=['Predicted'], margins = True)
true_rate(SVMpred1, list(test['label']))


SVM2 = svm.SVC(C = 1, kernel='poly', degree=3, gamma='auto')
SVM2.fit(train.iloc[idx1,[0,1,2,3,5,6]], train['label'].iloc[idx1])
SVMpred2 = SVM2.predict(test.iloc[:,[0,1,2,3,5,6]])
pd.crosstab(test['label'], pd.Series(SVMpred2), rownames=['Actual'], colnames=['Predicted'], margins = True)
true_rate(SVMpred2, list(test['label']))


SVM3 = svm.SVC(C = 1, kernel='sigmoid', degree=3, gamma='auto')
SVM3.fit(train.iloc[idx1,[0,1,2,3,5,6]], train['label'].iloc[idx1])
SVMpred3 = SVM3.predict(test.iloc[:,[0,1,2,3,5,6]])
pd.crosstab(test['label'], pd.Series(SVMpred3), rownames=['Actual'], colnames=['Predicted'], margins = True)
true_rate(SVMpred3, list(test['label']))