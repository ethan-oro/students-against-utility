import sys, os
import plotly.plotly as py
import plotly.graph_objs as go
sys.path.append('./../data_processing/')
from dataprocess import *
from sklearn import linear_model
from sklearn import svm
from sklearn import ensemble
from sklearn import discriminant_analysis
NUM_TRIALS = 100

def main():
    # print('-- PART I --')
    # data_first = grab_data_spend()
    # for key in data_first['full_y'].keys():
    #     print(key)
    #     spend_model = Model(type="XGBoost", regularization = False)
    #
    #     data_first = grab_data_spend()
    #     data_new = data_first
    #     data_new['full_y'] = data_first['full_y'][key]
    #
    #     avg_score_train, avg_score_test = multiple_splits(spend_model, data_new)
    #     print('Average Training Score: ' + str(avg_score_train))
    #     print('Average Testng Score: ' + str(avg_score_test))

    perform_model = Model(type='full')
    data_second = grab_data()
    avg_score_train, avg_score_test = multiple_splits(perform_model, data_second)
    print('-- RESULTS --')
    print('Average Training Score: ' + str(avg_score_train))
    print('Average Testng Score: ' + str(avg_score_test))

    return

    model_list = [ "linear_regression", 'SVM', 'XGBoost', 'BaggingRegressor', 'RandomForest', 'Lasso', 'AdaBoostRegressor', 'ExtraTreesRegressor']

    n_estimators=100
    subsample=1.0

    results = collections.defaultdict(tuple)
    for model in model_list:
        perform_model = Model(type=model, n_estimators=n_estimators, subsample=subsample)
        data_second = grab_data()
        avg_score_train, avg_score_test = multiple_splits(perform_model, data_second)
        results[model] = (avg_score_train, avg_score_test)
    for name, results in results.items():
        print('-- ', name ,' --')
        print('Average Training Score: ' + str(results[0]))
        print('Average Testng Score: ' + str(results[1]))


    #
    # test_score = np.zeros((n_estimators,), dtype=np.float64)
    #
    # clf = perform_model.model
    # for i, y_pred in enumerate(clf.staged_predict(perform_model.x_test)):
    #     test_score[i] = clf.loss_(perform_model.y_test, y_pred)
    #
    #
    # train = go.Scatter(x=np.arange(n_estimators) + 1,
    #                    y=clf.train_score_,
    #                    name='Training Set Deviance',
    #                    mode='lines',
    #                    line=dict(color='blue')
    #                   )
    # test = go.Scatter(x=np.arange(n_estimators) + 1,
    #                   y=test_score,
    #                   mode='lines',
    #                   name='Test Set Deviance',
    #                   line=dict(color='red')
    #                  )
    #
    # layout = go.Layout(title='Deviance',
    #                    xaxis=dict(title='Boosting Iterations'),
    #                    yaxis=dict(title='Deviance')
    #                   )
    # fig = go.Figure(data=[test, train], layout=layout)
    # pio.write_image(fig, 'fig1.png')
    #
    # print('finished plotting')
    #
    #
    #
    #
    # numIters = 20
    # n_estimators=100
    # subsample=1.0
    # params = []
    # for iter in range(0, numIters):
    #     perform_model = Model(type='XGBoost', n_estimators=n_estimators, subsample=subsample)
    #     data_second = grab_data()
    #     avg_score_train, avg_score_test = multiple_splits(perform_model, data_second)
    #     # print(perform_model.model.estimators_.shape)
    #     # tree = perform_model.model.estimators_[0, 0].tree_
    #     # leaf_mask = tree.children_left == -1
    #     # w_i = tree.value[leaf_mask, 0, 0]
    #     params.append(perform_model.model.estimators_)
    #     print (perform_model.model.estimators_.shape)
    #     print (type(perform_model.model.estimators_))
    #     print (type(perform_model.model.estimators_[0, 0].tree_))
    #
    # # estimators = []
    # # for param in params:
    #
    # model = Model(type='XGBoost', n_estimators=n_estimators, subsample=subsample)
    # # model.set_params()
    # sum_score_train = 0
    # sum_score_test = 0
    # for i in range(NUM_TRIALS):
    #     score_train, score_test = model.train(data)
    #     sum_score_train += score_train
    #     sum_score_test += score_test
    #     if noisy:
    #         print('---')
    #         print(score_train)
    #         print(score_test)
    # avg_score_train = sum_score_train / NUM_TRIALS
    # avg_score_test = sum_score_test / NUM_TRIALS
    #
    # print('-- RESULTS --')
    # print('Average Training Score: ' + str(avg_score_train))
    # print('Average Testng Score: ' + str(avg_score_test))
    #
    #
    #
    # for n_estimators in range(60, 100, 10):
    #     for subsample in [0.6, 0.7, 0.8, 0.9, 1.0]:
    #         perform_model = Model(type='XGBoost', n_estimators=n_estimators, subsample=subsample)
    #         data_second = grab_data()
    #
    #         avg_score_train, avg_score_test = multiple_splits(perform_model, data_second)
    #         print('-- ', models[0] , ': n_estimators: ', n_estimators, '; subsample: ',subsample, ' --')
    #         print('Average Training Score: ' + str(avg_score_train))
    #         print('Average Testng Score: ' + str(avg_score_test))


def multiple_splits(model, data, noisy = False):
    sum_score_train = 0
    sum_score_test = 0
    for i in range(NUM_TRIALS):
        score_train, score_test = model.train(data)
        sum_score_train += score_train
        sum_score_test += score_test
        if noisy:
            print('---')
            print(score_train)
            print(score_test)
    avg_score_train = sum_score_train / NUM_TRIALS
    avg_score_test = sum_score_test / NUM_TRIALS

    return avg_score_train, avg_score_test

class Model(object):
    def __init__(self, type = "linear_regression", regularization = False, n_estimators = 100, subsample = 1.0):
        if type == "linear_regression":
            if regularization:
                self.model = linear_model.Ridge()
            else:
                self.model = linear_model.LinearRegression(normalize=True)
        elif type == "SVM":
            self.model = svm.SVR()
        elif type == 'XGBoost':
            self.model = ensemble.GradientBoostingRegressor(n_estimators=n_estimators, subsample=subsample)
        elif type == 'BaggingRegressor':
            self.model = ensemble.BaggingRegressor()
        elif type == 'RandomForest':
            self.model = ensemble.RandomForestRegressor()
        elif type == "AdaBoostRegressor":
            self.model = ensemble.AdaBoostRegressor()
        elif type == 'ExtraTreesRegressor':
            self.model = ensemble.ExtraTreesRegressor()
        elif type == 'Lasso':
            self.model = linear_model.Lasso()
        elif type == "qda":
            self.model = discriminant_analysis.QuadraticDiscriminantAnalysis()
        elif type == "lda":
            self.model = discriminant_analysis.LinearDiscriminantAnalysis()
        elif type == 'full':
            self.model = ensemble.BaggingRegressor(base_estimator=ensemble.GradientBoostingRegressor())


    def _transform_data(self, dataframe_x, dataframe_y, train_split = 0.8):
        m,n = dataframe_x.shape

        x = np.array(dataframe_x)
        y = np.array(dataframe_y)
        random_state = np.random.get_state()
        np.random.shuffle(x)
        np.random.set_state(random_state)
        np.random.shuffle(y)
        split_ind = int(train_split*m)
        x_train = x[:split_ind,:]
        y_train = y[:split_ind]
        x_test = x[split_ind:,:]
        y_test = y[split_ind:]

        means = np.nanmean(x_train, axis=0)
        x_train = np.nan_to_num(x_train)
        x_test = np.nan_to_num(x_test)

        bad_inds_train = np.where(x_train == 0)
        bad_inds_test = np.where(x_test == 0)

        x_train[bad_inds_train] = np.take(means, bad_inds_train[1])
        x_test[bad_inds_test] = np.take(means, bad_inds_test[1])

        # std = x_train.std(axis=0)

        # means = means.reshape((n,1)).T
        # std = std.reshape((n,1)).T

        # x_train = (x_train - means) / std
        # x_test = (x_test - means) / std

        return (x_train, y_train, x_test, y_test)

    def train(self, data, data_key = 'highschool', noisy = False):
        # data_key is one of 'full', 'highschool', 'middleschool', 'elementary'
        data_x = data['%s_x'%data_key]
        data_y = data['%s_y'%data_key]
        self.x_train, self.y_train, self.x_test, self.y_test = self._transform_data(data_x, data_y)
        self.model.fit(self.x_train, self.y_train)
        if noisy:
            print(self.model.predict(self.x_test))
            print('--')
            print(self.y_test)
            print('--')
            print(self.model.predict(self.x_test) - self.y_test)
        score_train = self.model.score(self.x_train, self.y_train)
        score_test = self.model.score(self.x_test, self.y_test)

        return score_train, score_test






if __name__ == '__main__':
    main()
