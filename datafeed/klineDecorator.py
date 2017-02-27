'''A K-line data decorator which takes tick-by-tick datafeed and deliver
to subscriber when minite line collected.
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
import collections
import datetime as dt
import logging

# third-party modules
import numpy  as np
import pandas as pd

# customized modules
import datafeed.engine as dEngine
import datafeed.subpub as subpub

# customize logging configure
logging.basicConfig( format='[%(levelname)s] %(message)s',
        level=logging.DEBUG )

class KlineDecorator( subpub.Subscriber ):
    '''Data decorator for K-lines. It implements the interfaces of datafeed.subpub.Subscriber.
    '''

    def __init__( self, subscriber, binSize=1 ):
        '''Initialize the K-line filter.

Parameters
----------
subscriber : datafeed.subpub.Subscriber
    Data subscriber to deliver the data;
binSize : int
    periods of the k-lines in minute, by default check 1-minute k-line.
        '''
        super( KlineDecorator, self ).__init__()

        # hold the subscriber
        self.subscriber = subscriber

        # maintain the k-line book-keeping information
        self.binSize = binSize
        self.klines  = self._initializeKLineDict()
        self.prevDatetime = None


    def _initializeKLineDict( self ):
        '''Initialize k-line dict.

Returns
-------
klineDict : collectoins.defaultdict
    A kline dict as a collections.defaultdict with instrument identifiers the keys and
dict's as values. The value dict are keyed on
* openPrice - open price;
* highPrice - high price;
* lowPrice  - low price;
* and closePrice - close price.
        '''
        return collections.defaultdict( lambda: { 'openPrice': np.nan,
                'highPrice': np.nan, 'lowPrice': np.nan, 'closePrice': np.nan } )


    # Interfaces from datafeed.subpub.Subscriber
    def onData( self, data ):
        '''Get notification from the publisher.

Parameters
----------
data : pandas.DataFrame
    Messages from publisher as a pandas DataFrame.

Exceptions
----------
raise Exception when error occurs.
        '''
        currentDatetime = data.tradeDate.iloc[ 0 ]
        instIds = data.index

        # update kline dict
        for instId in instIds:
            record = data.ix[ instId ]
            price  = record.price
            if np.isnan( self.klines[ instId ][ 'openPrice' ] ):
                self.klines[ instId ][ 'openPrice' ] = price

            self.klines[ instId ][ 'closePrice' ] = price

            currentHighPrice = self.klines[ instId ][ 'highPrice' ]
            currentLowPrice  = self.klines[ instId ][ 'lowPrice' ]
            if np.isnan( currentHighPrice ) or price > currentHighPrice:
                self.klines[ instId ][ 'highPrice' ] = price

            if np.isnan( currentLowPrice ) or price < currentLowPrice:
                self.klines[ instId ][ 'lowPrice' ] = price

        # update kline data
        if self.prevDatetime is None:
            self.prevDatetime = currentDatetime
        elif ( currentDatetime - self.prevDatetime ).total_seconds() >= self.binSize * 60:
            self.prevDatetime = currentDatetime
            # clear all k-line data and delivery the datafeed to strategy
            # convert kline dict into a pandas.DataFrame
            klineDf = pd.DataFrame( self.klines ).T
            # append datetime as a string in the format %Y%m%d%M%H
            klineDf[ 'timestamp' ] = currentDatetime.strftime( '%Y%m%d%H%M' )
            print( klineDf )
            # deliver the DataFrame
            self.subscriber.onData( klineDf )

            # reset kline dict
            self.klines = self._initializeKLineDict()


    def getSubscribedTopics( self ):
        '''Topics to subscribe.

Returns
-------
topics : list of str
    A list of topics to subscribe.
        '''
        return self.subscriber.getSubscribedTopics()


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
        return self.subscriber.getSubscribedDataFields()
