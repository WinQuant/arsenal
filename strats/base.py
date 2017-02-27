'''This is the base strategy module of for the quant trading platform.
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
import numpy  as np
import pandas as pd

# customized modules
import datafeed.subpub as subpub

class Strategy( subpub.Subscriber ):
    '''Base class for the Strategy.
    '''
    # Signal
    CLOSED = 0
    LONG   = 1
    SELL   = -1
    NO_SIGNAL = np.nan


    def __init__( self ):
        '''Initialize the strategy object with a pandas time series representing mtm's.
        '''
        super( Strategy, self ).__init__()
        self.mtms = pd.Series()
        # actions and signals for generated orders
        self.actions = {}
        self.signals = {}


    @classmethod
    def instantiateStrategy( cls, model ):
        '''Instantiate a strategy by the given model. The strategy should know
how to interpret the model object.

Paramters
---------
model : pandas.Series
    A pandas Series representing the model.

Returns
-------
strategy : Strategy
    A Strategy object with the given model.
        '''


    @classmethod
    def isSignalIssued( cls, signal ):
        '''Check whether any signal is issued.

Parameters
----------
signal : int
    Indicator of signal type defined in this class.

Returns
-------
signalIssued : boolean
    A boolean indicating whether the signal is issued.
        '''
        return not np.isnan( action )


    def openMarket( self, asOfDate ):
        '''Initialize the market when open.

Parameters
----------
asOfDate : str
    trading date in the format %Y%m%d.
        '''


    def closeMarket( self, asOfDate, closeInfo ):
        '''Finalize one day's PnL's when market closes.

Parameters
----------
asOfDate  : datetime.date or datetime.datetime
    date of the mark-to-market;
closeInfo : pandas.DataFrame
    close information indexed by security identifiers.

Returns
-------
mtm : float
    mark-to-market value.
        '''
        mtm = self.mtm( closeInfo )
        self.mtms[ asOfDate ] = mtm

        return mtm


    def mtm( self, closeInfo ):
        '''Calculate mark-to-market with the closed price.

Parameters
----------
closeInfo : pandas.DataFrame
    Close information.

Returns
-------
mtm : float
    mark-to-market value.
        '''
        return 0.0


    def getMtms( self ):
        '''Get the generated mtm time series.

Returns
-------
mtms : pandas.Series
    Mark-to-market time series.
        '''
        return self.mtms


    # interfaces from subscriber
    def onData( self, datafeed ):
        '''Accept new data feed and generate orders if needed.

Parameters
----------
datafeed : pandas.DataFrame
    Issue the new data feed and get the orders to be placed.

Returns
-------
orderList : list of execution.order.Order
    A list of orders to be placed.
        '''
        return []


    def onTradeReturn( self, datafeed ):
        '''Accept trade notification.

Parameters
----------
datafeed : pandas.DataFrame
    Trade execution notification in pandas DataFrame.
        '''


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
        return [ '' ]


    def getSubscribedDataFields( self ):
        '''Data fields to subscribe.

Returns
-------
subscribedFields : list of str or None
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
        return self.signals


    def getActions( self ):
        '''Get actions for generated orders.

Returns
-------
actions : dict
    Generated actions keyed by data number.
        '''
        return self.actions
