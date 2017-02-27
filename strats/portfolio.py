'''This scripts abstract the strategy portfolio.
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
import datetime as dt
import logging

# third-party modules
import matplotlib.pyplot as plt
import pandas   as pd

# customized modules
import strats.base as strats

# customize logging configure
logging.basicConfig( format='[%(levelname)s] %(message)s', level=logging.INFO )

class Portfolio( strats.Strategy ):
    '''A portfolio is a collection of strategies to execute.
    '''

    def __init__( self, executionEngine, isBacktest=False ):
        '''Initialize a portfolio object.

Parameters
----------
executionEngine : execution.engine.ExecutionEngine
    execution engine object to run issue the order.
        '''
        super( Portfolio, self ).__init__()
        # all strategies
        self.strategies = []

        # topics to subscribers mapping, keyed by topic and value sets of
        # subscribers
        self.topicsToSubscribers = {}

        # execution engine
        self.executionEngine = executionEngine
        # wire the callback functions and the execution unit up
        self.executionEngine.setCallbacks(
                onTradeReturn=self.onTradeReturn )

        # a flag indicates whether the strategy is for backtest or not
        # for backtest purpose, some bookkeeping stats are maintained;
        # otherwise, redundant steps are eliminated to speed the execution up.
        self.isBacktest = isBacktest

        # order to strategy mapping
        self.orders = {}


    def addStrategy( self, strategy ):
        '''Add one more stratgey to the portfolio.

Parameters
----------
strategy : starts.base.Strategy
    The strategy object to be added into the portfolio.
        '''
        # update topics list
        topics = strategy.getSubscribedTopics()
        for topic in topics:
            if topic not in self.topicsToSubscribers:
                self.topicsToSubscribers[ topic ] = set()
            logging.debug( 'Add topic to strategy mapping {t:s}'.format(
                    t=topic ) )
            self.topicsToSubscribers[ topic ].add( strategy )

        self.strategies.append( strategy )


    def mtm( self, closeInfo ):
        '''Calculate the mark-to-market with the closed price.

Paramters
---------
closeInfo : pandas.DataFrame
    Close information.

Returns
-------
mtm : float
    mark-to-market value.
        '''
        mtm = 0.0
        for s in self.strategies:
            mtm += s.mtm()

        return mtm


    def openMarket( self, asOfDate ):
        '''Initialize the market when open.

Parameters
----------
asOfDate : str
    trading date in the format %Y%m%d.
        '''
        for s in self.strategies:
            s.openMarket( asOfDate )


    def closeMarket( self, timestamp, closeInfo ):
        '''Finalize one day's PnL's when market close.

Parameters
----------
timestamp : str
    datetime of the mark-to-market in the format %Y%m%d;
closeInfo : pandas.DataFrame
    close information by security indexed by identifiers.

Returns
-------
mtm : float
    mark-to-market value.
        '''
        mtm = 0.0
        for s in self.strategies:
            mtm += s.closeMarket( timestamp, closeInfo )

        self.mtms[ timestamp ] = mtm

        return mtm


    def showResults( self, figsize=( 12, 8 ), lineWidth=1 ):
        '''Plot show PnL in plot.

Parameters
----------
figsize : tuple
    Figure size;
lineWidth : int
    Line width of the marker.
        '''
        pnls = pd.Series()
        for s in self.strategies:
            pnls = pnls.add( s.getPnls(), fill_value=0 )

        nData = len( pnls )
        if nData > 0:
            # plot PnL's
            xTickStep = int( nData / 8 )
            rotation  = '30'

            fig, ax = plt.subplots( figsize=figsize )
            ax.plot( range( nData ), pnls, c='b', label="P&L's" )

            # labels and legends
            ax.set_ylabel( "P & L's" )
            ax.set_xticks( range( 0, nData, xTickStep ) )
            ax.set_xticklabels( pnls.index[ :: xTickStep ], rotation=rotation )
            axHandles, axLabels = ax.get_legend_handles_labels()
            ax.legend( axHandles, axLabels, loc=0 )
        else:
            logging.warn( "No PnL's recorded, please check whether the strategies ran in backtest mode." )


    # Subscriber interface
    def onData( self, datafeed ):
        '''Notify the relevant subscribers about the data change.

Parameters
----------
datafeed : pandas.DataFrame
    Data feed to notify the change, indexed by securities identifiers.
        '''
        subscribers = self.getSubscribersOnTopics( set( datafeed.index ) )

        for s in subscribers:
            if s.isActive():
                orders = s.onData( datafeed )
                for o in orders:
                    # keep an eye on all the orders submitted.
                    oid = self.executionEngine.placeOrder( o,
                            onOrderFilled=s.onOrderFilled )
                    self.orders[ oid ] = s

        if self.isBacktest:
            timestamp = datafeed.timestamp.iloc[ 0 ]
            # if need to calculate the mtm each step
            self.closeMarket( timestamp, datafeed )


    # CTP execution unit callbacks
    def onTradeReturn( self, orderRefId, orderSysId, tradeId, price,
            volume, tradeDate, tradeTime, orderLocalId, seqNo ):
        if orderRefId in self.orders:
            self.orders[ orderRefId ].onTradeReturn( orderRefId )


    def getSubscribedTopics( self ):
        '''Get all subscribed topics/security ID's from all the containing strategies.
        '''
        return list( self.topicsToSubscribers )


    def getSubcribedDataFields( self ):
        '''Get all subscribed data fields from all the containing strategies.
        '''
        dataFields = set()
        for s in self.strategies:
            fields = s.getSubscribedDataFields()
            if fields is None:
                logging.warning( 'Skip all the rest strategies for the strategy {s:s} subscribes all.'.format(
                        s=s ) )
                dataFields = None
                break
            else:
                dataFields.update( fields )

        return  None if dataFields is None else list( dataFields )


    def getSubscribersOnTopics( self, topics ):
        '''Get all subscribers on the given topics.

Parameters
----------
topics : list of str
    All topics whose subscribers to get.

Returns
-------
subscribers : list of strats.base.Strategy
    All subscribers on the given topics.
        '''
        subscribers = set()

        for topic in topics:
            subscribers = subscribers.union( self.topicsToSubscribers.get(
                    topic, set() ) )

        return subscribers
