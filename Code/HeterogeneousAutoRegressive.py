import statsmodels.api as sm
import numpy as np
import dataUtils

class HARmodel:

    def __init__(self):

        self.fitted = False
        self.modelType = "HAR"

    def fit(self, dataHAR, silent = True):

        modelSetUp = sm.OLS(dataHAR['Y'], sm.add_constant(dataHAR[['X1', 'X5', 'X22']]))
        self.model = modelSetUp.fit()

        if not silent:
            print(self.model.summary())

        self.fitted = True

    def oneStepAheadForecast(self, historicDataVector):

        const  = self.model.params[0]
        beta_d = self.model.params[1]
        beta_w = self.model.params[2]
        beta_m = self.model.params[3]

        estimate = const + beta_d * historicDataVector[-1] + \
            beta_w * sum(historicDataVector[-5:-1])/4 + beta_m * sum(historicDataVector[-22:-1])/21

        return estimate

    def multiStepAheadForecast(self, data, forecastHorizon, startIndex, 
                                            windowMode, windowSize = 0):

        assert startIndex - 22 > 0
        assert windowMode.upper() in ["EXPANDING", "ROLLING", "FIXED"], "Window Mode not recognized"

        if windowMode.upper() == "EXPANDING":
            newxTrain = np.concatenate([data.xTrain, data.xTest[:startIndex]])
            newdataHAR = dataUtils.convertHAR(newxTrain[:])
            self.fit(newdataHAR, silent = True)
        elif windowMode.upper() == "ROLLING":
            newxTrain = np.concatenate([data.xTrain, data.xTest[:startIndex]])
            newdataHAR = dataUtils.convertHAR(newxTrain[-windowSize:])
            self.fit(newdataHAR, silent = True)
        else: pass


        historicDataVector = data.xTest[startIndex - 22: startIndex]

        def predict(forecastHorizon, forecast, historicDataVector):

            backlog = np.append(historicDataVector, forecast)

            forecast.append(self.oneStepAheadForecast(backlog))

            return predict(forecastHorizon, forecast, historicDataVector) if len(forecast) < forecastHorizon \
                else np.array(forecast)
        
        multiStepAheadForecast = predict(forecastHorizon, [], historicDataVector)

        return multiStepAheadForecast.reshape(forecastHorizon, 1)