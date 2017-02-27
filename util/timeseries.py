'''This file contains utility functions related to TimeSeries manipulation.
'''

'''
Copyright (c) 2017, WinQuant Information and Technology Co. Ltd.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

# built-in modules
import logging

# third-party modules
import pandas as pd
import numpy  as np

# customized modules

# customize logging configure
logging.basicConfig( format='[%(levelname)s] %(message)s', level=logging.INFO )

def predictAr( order, series, withConstant=True ):
    '''Predict AR model with the given order and series.
In the series, the latest data comes first, i.e. data is arranged from left to right.

Parameters
----------
order : int
    Order of the Auto-regressive model to fit;
series : list of number
    Series to fit the auto-regressive model;
withConstant : boolean
    A boolean indicator whether include constant when fitting the AR model.

Returns
-------
pred : float
    One-step out-of-sample predict with the fitted auto-regressive model.

Exceptions
----------
raise Exception when the dimension of the given series is less than the order
of the AR model to be fitted.
    '''
    n = len( series )
    if n < order:
        raise Exception( 'Series dimension ({n:d}) should be greater than the expected AR order {o:d}.'.format(
                n=n, o=order ) )
    else:
        nTraining = n - order
        Y = series[ : nTraining ]
        X = []
        for i in range( order ):
            X.append( series[ i + 1 : i + 1 + nTraining ] )

        # if constant needed, padding the constant items
        if withConstant:
            X.append( [ 1 ] * nTraining )

        X = np.matrix( X ).T
        Y = np.matrix( Y ).T

        # refer to Wikipedia.org for the estimation of all the parameters
        # https://en.wikipedia.org/wiki/Linear_regression#Least-squares_estimation_and_related_techniques
        try:
            beta = np.linalg.inv( X.T * X ) * X.T * Y

            predict = np.matrix( series[ : order ] + [ 1 ] if withConstant else \
                        [] ) * beta

            result = predict.A[ 0 ][ 0 ]
        except Exception as e:
            logging.error( 'Linear Algebra Error %s.', e )
            result = series[ -1 ]

        return result


def convertDfToPanel( df, itemAxisColNames, majorAxisColName, minorAxisColName ):
    '''Convert DataFrame to Panel, whose columns become the item axis of the Panel.
For each DataFrame in the Panel, minor axis are securities identifiers and rows indexed
by data date.

Parameters
----------
df : pandas.DataFrame
    DataFrame of the input data;
itemAxisColNames : list of str
    column names in the original DataFrame as the item axis in the output Panel;
majorAxisColName : str
    column name in the original DataFrame as the major axis in the output Panel;
minorAxisColName : str
    column name in the original DataFrame as the minor axis in the output Panel.

Returns
-------
panel : pandas.Panel
    Converted panel.
    '''
    data = {}
    for col in itemAxisColNames:
        df = df[ majorAxisColName, minorAxisColName, col ].pivot(
                majorAxisColName, minorAxisColName, col )
        data[ col ] = df

    return pd.Panel( data )


def reshapeDf( dataDf, majorAxisColName, minorAxisColName, valueColName ):
    '''Reshape a pandas DataFrame with three columns into a new one with major axis
column, minor axis column, and data column given respectively.

Parameters
----------
dataDf : pandas.DataFrame
    original data in pandas DataFrame;
majorAxisColName : str
    major axis column name;
minorAxisColName : str
    minor axis column name;
valueColName : str
    value column name.

Returns
-------
newDf : pandas.DataFrame
    reshaped DataFrame with majorAxisColumn sorted acsendingly.
    '''
    nrow, ncol = dataDf.shape

    if ncol > 3:
        logging.warn( 'Reshape DataFrame, only {mac:s}, {mic:s}, and {dc:s} reserved, others are dropped.'.format(
                mac=majorAxisColName, mic=minorAxisColName, dc=valueColName ) )
    elif ncol < 3:
        raise Exception( 'DataFrame reshape requires a 3-column input.' )

    series = []
    groupedDf = df.groupby( minorAxisColName )
    for col, subDf in groupedDf:
        s = pd.Series( subDf[ valueColName ], index=subDf[ majorAxisColName ],
                name=col )
        s.sort_index( inplace=True )
        series.append( s )

    return pd.DataFrame( series )


def ewma( ts, alpha ):
    '''EWMA of the given series data.

Parameters
----------
data : pandas.Series
    Data to estimate;
alpha : float
    exponentially moving average argument.

Returns
-------
ewma : float
    EWAM of the given series.
    '''
    nData   = len( ts )
    weights = pd.Series( 1 - alpha, index=ts.index )
    exp     = pd.Series( range( nData - 1, -1, -1 ), index=ts.index )
    expWeights = weights.pow( exp )

    return ( alpha * expWeights * ts ).sum()
