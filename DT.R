library(ISLR)
library(caret)

#randomly pick train set
train = read.csv('/Users/jiahuiwu/Desktop/501/portfolio/DT_train.csv')
test = read.csv('/Users/jiahuiwu/Desktop/501/portfolio/DT_test.csv')
set.seed(40)
idx1 = sample(1:nrow(OJ), size = round(0.8*nrow(OJ)))
idx2 = sample(1:nrow(OJ), size = round(0.8*nrow(OJ)))
idx3 = sample(1:nrow(OJ), size = round(0.8*nrow(OJ)))


library(tree)
tree1 = tree(count~., data = train[idx1,])
summary(tree1)
plot(tree1)
text(tree1, pretty = 0)

tree2 = tree(count~., data = train[idx2,])
summary(tree2)
plot(tree2)
text(tree2, pretty = 0)

tree3 = tree(count~., data = train[idx3,])
summary(tree3)
plot(tree3)
text(tree3, pretty = 0)
