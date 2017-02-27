'''This is the base strategy module for stock trading.
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
import copy
import logging

# third-party modules
import numpy  as np
import pandas as pd

# customized modules
import execution.order as eo
import strats.base as base
import strats.book as book
import util.calendar as uc
import util.stock    as us


class StockStrategy( base.Strategy ):
    '''Base class for stock strategies.
    '''

    def __init__( self, totalAsset, dataSource, executionEngine, hedger=None,
                assetAllocator=None, freq=1 ):
        '''Initialize the strategy object with a pandas time series representing mtm's.

Parameters
----------
totalAsset : float
    Total asset used for the strategy;
dataSource : data.api.stocks.DataSource
    data source for historical data;
universe : data.api.universe.StockUniverse
    stock universe generator;
executionEngine : execution.stockBacktestEngine.StockBacktestExecutionEngine
    stock backtest execution engine;
hedger : hedger.Hedger
    hedging leg of the stock strategy;
assetAllocator : strats.stocks.assetAllocator.AssetAllocator
    asset allocation strategy;
freq : int
    the frequency to adjust positions.
        '''
        super( StockStrategy, self ).__init__()

        # pandas DataFrame with position information and total asset when close.
        self.tradingHistory = pd.DataFrame( columns=[ 'Date', 'Position', 'Asset' ] )
        self.tradingHistory.set_index( [ 'Date' ], inplace=True )

        self.position = book.PortfolioPosition( totalAsset )

        # data source
        self.dataSource      = dataSource
        # execution engine
        self.executionEngine = executionEngine
        # asset allocation strategy
        self.assetAllocator  = assetAllocator
        # hedger
        self.hedger = hedger
        # position adjustment frequencey
        self.freq  = freq
        self.round = 0

        # a collection of executed orders
        self.orders = {}

        # trading calendar
        self.calendar      = uc.AShareTradingCalendar( self.dataSource, startDate=uc.DEFAULT_TS_START_DATE )
        # suspending dates
        self.suspendingDates = self.dataSource.getSuspensionDates( startDate=uc.DEFAULT_TS_START_DATE )
        # dividend information
        dividendInfo      = self.dataSource.getDividendInformation( startDate=uc.DEFAULT_TS_START_DATE )
        self.dividendInfo = dividendInfo.groupby( 'EX_DT' )
        # right issue information
        rightIssueInfo      = self.dataSource.getRightIssueInformation( startDate=uc.DEFAULT_TS_START_DATE )
        self.rightIssueInfo = rightIssueInfo.groupby( 'S_RIGHTSISSUE_EXDIVIDENDDATE' )

        # delist information
        self.delistedStocks = self.dataSource.getDelistedStocks( startDate=uc.DEFAULT_TS_START_DATE )


    @classmethod
    def instantiateStrategy( cls, model ):
        '''Instantiate a strategy by the given model. The strategy should know how to
interpret the model object.

Parameters
----------
model : pandas.Series
    A pandas Series representing the model.

Returns
-------
strategy : StockStrategy
    A StockStrategy object with the given model.
        '''


    def openMarket( self, asOfDate ):
        '''Open market hook.

Parameters
----------
asOfDate : str
    Dividend data date in the format %Y%m%d.
        '''
        try:
            dividendInfo = self.dividendInfo.get_group( asOfDate )
        except KeyError:
            logging.warn( 'No dividends on {d:s}.'.format( d=asOfDate ) )
            dividendInfo = None

        try:
            rightIssueInfo = self.rightIssueInfo.get_group( asOfDate )
        except KeyError:
            logging.warn( 'No right issues on {d:s}.'.format( d=asOfDate ) )
            rightIssueInfo = None

        stockPositions = self.position.getPositions()
        for stock in stockPositions.index:
            # this stock is divided on the given date.
            dividend10,   right10         = self.getDividend( dividendInfo, stock )
            rightIssue10, rightIssuePrice = self.getRightIssue( rightIssueInfo, stock )
            self.position.adjustPrice( stock, dividend10=dividend10, right10=right10,
                    rightIssue10=rightIssue10, rightIssuePrice=rightIssuePrice )


    def closeMarket( self, asOfDate ):
        '''Fianlize one day's PnL when market closes.

Parameters
----------
asOfDate : str
    date of mark-to-market in the format %Y%m%d.
        '''
        closeInfo  = self.dataSource.getStockDailyData( startDate=asOfDate, endDate=asOfDate )
        totalAsset = self.position.getTotalAsset( closeInfo )

        if self.hedger is not None:
            self.hedger.closeMarket( asOfDate )
            totalAsset += self.hedger.getTotalAsset( asOfDate )

        # add the given date's position information and total asset to the book
        # keeping data structure
        self.tradingHistory.ix[ asOfDate ] = pd.Series( [ self.position, totalAsset ],
                index=[ 'Position', 'Asset' ] )
        self.position = copy.deepcopy( self.position )


    def onData( self, asOfDate, assetWeight=1.0 ):
        '''Accept new data feed and generate orders if needed.

Parameters
----------
asOfDate : datetime.date
    Trading date;
assetAllocation : float
    asset weight to allocate.

Returns
-------
orderList : list of execution.order.Order
    A list of orders to be placed.
        '''


    def datafeed( self, asOfDate ):
        '''Handle data feed.

Parameters
----------
asOfDate : datetime.date
    Trading date.
        '''
        self.openMarket( asOfDate )

        if self.round % self.freq == 0:
            if self.assetAllocator is not None:
                assetWeight = self.assetAllocator.allocateAsset( asOfDate )
            else:
                assetWeight = 1.0

            orders = self.onData( asOfDate, assetWeight=assetWeight )
            for o in orders:
                oid = self.executionEngine.placeOrder( o, onOrderFilled=self.onOrderFilled )
                self.orders[ oid ] = o

        self.closeMarket( asOfDate )

        # number of rounds fed
        self.round += 1


    def onOrderFilled( self, orderStatus ):
        '''Accept trade notification.

Parameters
----------
orderStatus : execution.order.OrderStatus
    Trade execution notification as an OrderStatus report.
        '''
        secId  = orderStatus.secId
        price  = orderStatus.executedPrice
        volume = orderStatus.orderSize
        commision = orderStatus.commision
        direction = orderStatus.orderDirection

        if direction == 1:
            # buy
            self.position.addPosition( secId, price, volume, commision )
        elif direction == -1:
            # sell
            self.position.deletePosition( secId, price, volume, commision )
        else:
            logging.warn( 'Unknown direction for the stock {secId:s}.'.format(
                    secId=secId ) )


    def stopLoss( self, newData ):
        '''Loss stopping policy.

Parameters
----------
newData : pandas.DataFrame
    New data feed to check the mark-to-market.

Returns
-------
stopLoss : boolean
    An indicator whether the stop loss process is triggered.
        '''
        return False


    def isActive( self ):
        '''Test is the strategy active.

Returns
-------
isActive : boolean
    An indicator whether this strategy is active, by default, True.
        '''
        return True


    def getSubscribedTopics( self ):
        '''Topics to subscribe.

Returns
-------
topics : list of str
    A list of topics to subscribe.
        '''
        return []


    def getSubscribedDataFields( self ):
        '''Data fields to subscribe.

Returns
-------
subscribedFileds : list of str or None
    List of str representing the fields to subscribe, if None returned,
subscribe all data fields.

Notes
-----
The following fields are accepted case insensitive.
* VOLUME
* PRICE
* BID
* ASK
* RT_VOLUME
* RT_PRICE
* etc.
        '''
        return None


    def getSignals( self ):
        '''Get signals for generated orders.

Returns
-------
signals : dict
    Generated signals keyed by data number.
        '''


    def getActions( self ):
        '''Get actions for generated orders.

Returns
-------
actions : dict
    Generated actions keyed by data number.
        '''


    def adjustPosition( self, asOfDate, weights, refPrices, positionRate=0.98,
                useWeightCapital=False, sellRefColumn=None, buyRefColumn=None,
                updateRefColumn=None, normalizeWeights=True, enableSab=False ):
        '''Adjust position of current stocks.

Parameters
----------
asOfDate : str
    Data date to do the position adjustment in the format %Y%m%d.
weights : pandas.Series
    New weights on the given stocks indexed by stock. Sum of all weights should be 1.
All stocks suspended on the given date should be weighted as 0.
Otherwise, the correctness is not guaranteed;
refPrices : pandas.DataFrame
    reference data to calculate current capital;
positionRate : float
    position water-mark, or say, the percentage of asset used;
useWeightCapital : bool
    use number in weights as monentary volume to buy/update;
sellRefColumn : str
    sell reference price column;
buyRefColumn : str
    buy reference price column;
updateRefColumn : str
    update reference price column;
normalizeWeights : bool
    normalize the weights or not;
enableSab : bool
    an indicator whether to sell all positions before buy.

Returns
-------
orders : list of execution.order.Order
    A list of orders to be placed.
        '''
        orders = []

        weights = weights[ weights >= 0 ]
        weights = weights.replace( [ np.inf, -np.inf ], np.nan ).dropna()
        # adjust total weights.
        if len( weights ) > 0 and normalizeWeights:
            weights = weights / weights.sum()

        prevTradingDate = self.prevTradingDate( asOfDate )
        nextTradingDate = self.nextTradingDate( asOfDate, n=self.freq )
        prevCloseInfo   = self.dataSource.getStockDailyData(
                startDate=prevTradingDate, endDate=prevTradingDate )
        suspendingStocks = self.getSuspendingStocks( asOfDate )
        # current total asset/capital is equal to previous trading day's
        # only 98% assets are used to do the trade by default,
        # in case the commision rate and slippage can not be
        # covered by the total asset.
        totalAsset = positionRate * self.position.getTotalAsset(
                refPrices=prevCloseInfo, excludeSuspended=suspendingStocks )

        stocksInBook = self.position.getStocksInBook()
        stocksToHold = set( weights.index )

        # check delisted stocks
        stocksToDelist  = set( self.delistedStocks.index[
                self.delistedStocks <= nextTradingDate ] )
        stocksForceSell = stocksInBook.intersection( stocksToDelist )

        # drop stocks cannot buy and cannot sell
        stocksCannotBuy  = self.getUpLimitStocks( refPrices )
        stocksCannotSell = self.getDownLimitStocks( refPrices )

        # drop all the stocks suspended and force sell delisted stocks the
        # next day
        if enableSab:
            stocksToSell = stocksInBook - suspendingStocks - stocksCannotSell
            stocksToBuy  = stocksToHold - suspendingStocks - stocksToDelist - stocksCannotBuy
            stocksToUpdate = set()
        else:
            stocksToSell = ( stocksInBook - stocksToHold - suspendingStocks - \
                    stocksCannotSell ).union( stocksForceSell )
            # for stocks to buy or to update, exclude those that are to be delisted
            stocksToBuy  = stocksToHold - stocksInBook - suspendingStocks - \
                    stocksToDelist - stocksCannotBuy
            stocksToUpdate = stocksToHold.intersection( stocksInBook ) - \
                    suspendingStocks - stocksToDelist - stocksCannotSell - \
                    stocksCannotBuy

        # extract buy sell reference prices
        if sellRefColumn is None:
            sellRefPrices = refPrices.S_DQ_CLOSE
        else:
            sellRefPrices = refPrices[ sellRefColumn ]

        if buyRefColumn is None:
            buyRefPrices = refPrices.S_DQ_CLOSE
        else:
            buyRefPrices = refPrices[ buyRefColumn ]

        if updateRefColumn is None:
            updateRefPrices = refPrices.S_DQ_CLOSE
        else:
            updateRefPrices = refPrices[ updateRefColumn ]

        # generate sell order for these stocks
        for stock in stocksToSell:
            o = eo.Order( stock, eo.Order.SELL, self.position.getPosition( stock ),
                    sellRefPrices.ix[ stock ] )
            orders.append( o )

        # generate buy order for the new weights
        for stock in stocksToBuy:
            if useWeightCapital:
                monetaryVolume = weights.ix[ stock ]
            else:
                monetaryVolume = totalAsset * weights.ix[ stock ]
            vwap = buyRefPrices.ix[ stock ]
            o = eo.Order( stock, eo.Order.BUY, us.roundVolume( monetaryVolume / vwap ), vwap )
            orders.append( o )

        # update existing positions
        for stock in stocksToUpdate:
            if useWeightCapital:
                monetaryVolume = weights.ix[ stock ]
            else:
                monetaryVolume = totalAsset * weights.ix[ stock ]
            # vwap = refPrices.S_DQ_CLOSE.ix[ stock ]
            vwap = updateRefPrices.ix[ stock ]
            targetVolume = us.roundVolume( monetaryVolume / vwap )

            diffVolume =  targetVolume - self.position.getPosition( stock )
            if diffVolume != 0:
                if diffVolume > 0:
                    direction = eo.Order.BUY
                    volume    = diffVolume
                else:
                    direction = eo.Order.SELL
                    volume    = -diffVolume

                o = eo.Order( stock, direction, volume, vwap )
                orders.append( o )

        # sort by direction, sell orders goes first
        orders = sorted( orders, key=lambda o: o.side )

        return orders


    def prevTradingDate( self, asOfDate, n=1 ):
        '''Calculate the previous trading date.

Parameters
----------
asOfDate : str
    Data date in the format %Y%m%d;
n : int
    number of historical days to look back. n should be positive.

Returns
-------
prevDate : str
    Previous trading date.

NOTE
----
This method will be deprecated, use self.calendar.prevTradingDate as an alternative.
        '''
        return self.calendar.prevTradingDate( asOfDate, n=n )


    def nextTradingDate( self, sinceDate, n=1 ):
        '''Calculate the next trading date.

Parameters
----------
sinceDate : str
    Data date in the format %Y%m%d;
n : int
    number of historical days to look back. n should be positive.

Returns
-------
nextDate : str
    Next trading date.

NOTE
----
This method will be deprecated, use self.calendar.nextTradingDate as an alternative.
        '''
        return self.calendar.nextTradingDate( sinceDate, n=n )


    def getTotalAsset( self, excludeSuspended=None ):
        '''Get total asset on the given date. If not available, return current total asset.

Parameters
----------
asOfDate : str
    Get the total asset on the given date. If None, return the last total asset.

Returns
-------
totalAsset : float
    Total asset on the given date.
        '''
        return self.position.getTotalAsset( excludeSuspended=excludeSuspended )


    def getSuspendingStocks( self, asOfDate ):
        '''Get all stocks that are suspended on the given date.

Parameters
----------
asOfDate : str
    data date in the format %Y%m%d.

Returns
-------
suspendingStocks : set of str
    A set of stock names that is suspended on the given date.
        '''
        return set( self.suspendingDates[ self.suspendingDates.S_DQ_SUSPENDDATE == asOfDate ].S_INFO_WINDCODE )


    def getDividend( self, dividendInfo, secId ):
        '''Extract the dividend informatoin of the given stock.

Parameters
----------
dividendInfo : pandas.DataFrame
    Dividend information in pandas DataFrame; if None,
no dividends available on the given dates;
secId : str
    name of the stock whose dividend information to extract.

Returns
-------
( dividend10, right10 ) : tuple of ( float, float )
    A tuple of extracted information with
    * dividend per 10 shares;
    * stock right per 10 shares.
        '''
        right10, dividend10 = 0.0, 0.0
        if dividendInfo is not None:
            stockDividend   = dividendInfo[ dividendInfo.S_INFO_WINDCODE == secId ]

            nRecords = len( stockDividend )
            if nRecords > 0:
                if nRecords > 1:
                    logging.warn( 'Multiple dividend records for {secId:s}.'.format(
                            secId=secId ) )
                else:
                    record = stockDividend.iloc[ 0 ]
                    right10    = record.STK_DVD_PER_SH * 10
                    dividend10 = record.CASH_DVD_PER_SH_PRE_TAX * 10

        return dividend10, right10


    def getRightIssue( self, rightIssueInfo, secId ):
        '''Extract the right issue information of the given stock.

Parameters
----------
rightIssueInfo : pandas.DataFrame
    Right issue information in pandas DataFrame;
secId : str
    name of the stock whose right issue information to extract.

Returns
-------
( rightIssueRate10, rightIssuePrice ) : ( float, float )
    A tuple of extracted information with
    * right issue rate per 10 shares;
    * right issue price per share.
        '''
        rightIssueRate10, rightIssuePrice = 0.0, 0.0
        if rightIssueInfo is not None:
            stockRightIssue = rightIssueInfo[ rightIssueInfo.S_INFO_WINDCODE == secId ]
     
            nRecords = len( stockRightIssue )
            if nRecords > 0:
                if nRecords > 1:
                    logging.warn( 'Multiple right issue records for {secId:s}.'.format(
                            secId=secId ) )
                else:
                    record = stockRightIssue.iloc[ 0 ]
                    rightIssueRate10 = record.S_RIGHTSISSUE_RATIO * 10
                    rightIssuePrice  = record.S_RIGHTSISSUE_PRICE

        return rightIssueRate10, rightIssuePrice


    def getUpLimitStocks( self, refPrices ):
        '''Get up limit stocks.

Parameters
----------
refPrices : pandas.DataFrame
    End-of-day reference prices.

Returns
-------
upLimitStocks : set of str
    all stocks at up limit prices.
        '''
        upLimitConditions = ( refPrices.S_DQ_HIGH == refPrices.S_DQ_OPEN ) & \
                            ( refPrices.S_DQ_OPEN == refPrices.S_DQ_CLOSE ) & \
                            ( refPrices.S_DQ_CLOSE == refPrices.S_DQ_LOW ) & \
                            ( refPrices.S_DQ_PCTCHANGE > 0 )

        return set( refPrices[ upLimitConditions ].index )


    def getDownLimitStocks( self, refPrices ):
        '''Get down limit stocks.

Parameters
----------
refPrices : pandas.DataFrame
    End-of-day reference prices.

Returns
-------
upLimitStocks : set of str
    all stocks at down limit prices.
        '''
        downLimitConditions = ( refPrices.S_DQ_HIGH == refPrices.S_DQ_OPEN ) & \
                              ( refPrices.S_DQ_OPEN == refPrices.S_DQ_CLOSE ) & \
                              ( refPrices.S_DQ_CLOSE == refPrices.S_DQ_LOW ) & \
                              ( refPrices.S_DQ_PCTCHANGE < 0 )

        return set( refPrices[ downLimitConditions ].index )
