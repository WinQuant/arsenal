'''This module defines the base class for measure-able risk metrics.
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

# third-party modules
import pandas as pd
import numpy  as np

# customized modules
import util.math as um


TRADING_DAYS_PER_YEAR = 252

class RiskMetric( object ):
    '''Base class of risk metrics.
    '''

    def __init__( self ):
        '''Initialize a risk metric object.
        '''


    def getValue( self, arg=None ):
        '''Get value of the risk metric.

Parameters
----------
arg : object
    extra argument used to calculate the risk metric.
        '''


class AnnualReturn( RiskMetric ):
    '''Annual returns of the given time series.
    '''

    def __init__( self, data ):
        '''Initialize an AnnualReturn risk metric object.

Parameters
----------
mtm : pandas.Series
    daily mark-to-market indexed by trading date as strings in the format %Y%m%d.
        '''
        super( AnnualReturn, self ).__init__()
        self.data = data


    def getValue( self ):
        '''Get value of the AnnualReturn.

Returns
-------
annualReturns : pandas.Series
    Annual return of the profit series in 0-1.
        '''
        return pd.Series( [ np.power( self.data.iloc[ i ] / self.data.iloc[ 0 ],
                TRADING_DAYS_PER_YEAR / ( i + 1 ) ) - 1 if i > 0 else np.nan for i in range( len( self.data ) ) ],
                index=self.data.index )


class AlphaBeta( RiskMetric ):
    '''Alpha-beta of the given profit returns to the risk free rate.
    '''

    def __init__( self, portfolioReturn, benchmarkReturn, riskfreeRate ):
        '''Initialize the AlphaBeta calculator with the portfolio data and a benchmark one.

Parameters
----------
portfolioReturn : pandas.Series
    annual returns indexed by trading date as strings in the format %Y%m%d;
benchmarkReturn : pandas.Series
    benchmark return indexed by trading date as strings in the format %Y%m%d.
Both of the arguments mush have the same length.
riskfreeRate : float
    risk-free interest rate.
        '''
        super( AlphaBeta, self ).__init__()
        self.portfolioReturn = portfolioReturn
        self.benchmarkReturn = benchmarkReturn
        self.riskfreeRate    = riskfreeRate


    def getValue( self ):
        '''Get value of the Alpha-beta regression.

Returns
-------
alphaBeta : pandas.DataFrame
    Alpha-beta pairs in a pandas DataFrame with columns Alpha, Beta, indexed by
trading dates as strings in the format %Y%m%d.
        '''
        alphas = []
        betas  = []
        for i in range( len( self.portfolioReturn ) ):
            if i == 0:
                alpha = np.nan
                beta  = np.nan
            else:
                n  = i + 1
                Xt = np.matrix( [ [ 1 ] * n, self.benchmarkReturn.iloc[ : n ] - self.riskfreeRate ] )
                X  = Xt.T
                Y  = np.matrix( [ self.portfolioReturn.iloc[ : n ] - self.riskfreeRate ] ).T

                alpha, beta = ( np.linalg.inv( Xt * X ) * Xt * Y ).T.A[ 0 ]

            alphas.append( um.infinitesimal( alpha ) )
            betas.append( um.infinitesimal( beta ) )

        return pd.DataFrame( { 'Alpha': alphas, 'Beta': betas }, index=self.portfolioReturn.index )


class Volatility( RiskMetric ):
    '''Volatility of the data.
    '''

    def __init__( self, data ):
        '''Initialize a volatility calculator.

Parameters
----------
data : pandas.Series
    daily returns indexed by trading date as strings in the format %Y%m%d.
        '''
        super( Volatility, self ).__init__()
        self.data = data


    def getValue( self ):
        '''Get value of the Volatility.

Returns
-------
volatility : pandas.Series
    Volatility of the given series.
        '''
        total = 0.0
        totalSquare = 0.0
        vol   = []
        n = 0

        for i in range( len( self.data ) ):
            daily = self.data.iloc[ i ]
            if not np.isnan( daily ):
                total += daily
                totalSquare += daily * daily

                n += 1
                if n == 1:
                    dailyVol = np.nan
                else:
                    dailyVol = totalSquare / (n - 1) - total * total / (n - 1) / n
            else:
                dailyVol = np.nan

            vol.append( dailyVol )

        volitility = np.sqrt( pd.Series( vol, index=self.data.index ) )
        volitility = volitility * np.sqrt( TRADING_DAYS_PER_YEAR )
        # in case too small number ruin the results
        volitility[ volitility.abs() < 1e-6 ] = 0.0

        return volitility


class InformationRatio( RiskMetric ):
    '''Information ratio of the data.
    '''

    def __init__( self, mtm, benchmark ):
        '''Initialize a volatility calculator.

Parameters
----------
mtm : pandas.Series
    daily mark-to-market indexed by trading date as strings in the format %Y%m%d.
benchmark : pandas.Series
    benchmark daily mark-to-market indexed by trading date as strings in the format %Y%m%d.
        '''
        super( InformationRatio, self ).__init__()
        self.mtm = mtm
        self.benchmark = benchmark

        pReturns = AnnualReturn( self.mtm )
        bReturns = AnnualReturn( self.benchmark )

        self.portfolioReturn = pReturns.getValue()
        self.benchmarkReturn = bReturns.getValue()

        volatility = Volatility( self.mtm.shift() / self.mtm - \
                self.benchmark.shift() / self.benchmark )
        self.volatility = volatility.getValue()


    def getValue( self ):
        '''Get value of the information ratio.

Returns
-------
informationRatio : pandas.Series
    Information ratio of the given series.
        '''
        improvement = ( self.portfolioReturn - self.benchmarkReturn ).fillna( 0 )
        volatility  = self.volatility
        ir = improvement / volatility
        ir.replace( [ np.inf, -np.inf ], np.nan, inplace=True )

        return ir


class SharpeRatio( RiskMetric ):
    '''Sharpe ratio of the data.
    '''

    def __init__( self, mtm, riskfreeRate ):
        '''Initialize a sharpe ratio calculator.

Parameters
----------
mtm : pandas.Series
    daily mark-to-market indexed by trading date as strings in the format %Y%m%d;
riskfreeRate : float
    risk-free interest rate.
        '''
        self.mtm = mtm
        self.rf  = riskfreeRate

        pReturns = AnnualReturn( self.mtm )
        self.portfolioReturn = pReturns.getValue()

        volatility = Volatility( self.mtm.shift() / self.mtm - riskfreeRate )
        self.volatility = volatility.getValue()


    def getValue( self ):
        '''Get value of the sharpe ratio.

Returns
-------
sharpeRatio : pandas.Series
    Sharpe ratio of the given series.
        '''
        improvement = ( self.portfolioReturn - self.rf ).fillna( 0 )
        volatility  = self.volatility
        sr = improvement / volatility
        sr.replace( [ np.inf, -np.inf ], np.nan, inplace=True )

        return sr


class MaximumDrawdown( RiskMetric ):
    '''Maximum draw-down rate calculator.
    '''

    def __init__( self, annualReturn ):
        '''Intialize maximum draw down calculator with a time series.

Parameters
----------
annualReturn : pandas.Series
    Annual return series indexed by trading date as strings in the format of %Y%m%d.
        '''
        self.annualReturn = annualReturn


    def getValue( self ):
        '''Get value of maximum draw-down.

Returns
-------
drawdown : pandas.DataFrame
    Maximum draw down with column MDD, startDate, endDate.
        '''
        mdds = []
        startDates = []
        endDates   = []

        maximumReturn   = 0.0
        maximumDrawdown = 0.0
        startDate   = None
        endDate     = None
        maxReturnDate = None
        for tradingDate in self.annualReturn.index:
            returnRate = self.annualReturn.ix[ tradingDate ]
            if maxReturnDate is None:
                maxReturnDate = tradingDate

            if returnRate > maximumReturn:
                maximumReturn = returnRate
                maxReturnDate = tradingDate
            elif maximumReturn - returnRate > maximumDrawdown:
                maximumDrawdown = maximumReturn - returnRate
                startDate = maxReturnDate
                endDate   = tradingDate

            mdds.append( maximumDrawdown )
            startDates.append( startDate )
            endDates.append( endDate )

        return pd.DataFrame( { 'MDD': mdds, 'StartDate': startDates,
                'EndDate': endDates }, index=self.annualReturn.index )
