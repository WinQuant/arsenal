'''A data feed engine for backtesting.
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

# third-party modeuls
import pandas as pd

# customized modules
import data.api.futures as futuresApi
import datafeed.engine  as dEngine

# customized logging configure
logging.basicConfig( format='[%(levelname)s] %(message)s',
        level=logging.DEBUG )

class BacktestDataPublisher( dEngine.DataPublisher ):
    '''Data publish engine for backtesting.
    '''

    def __init__( self, datafeed ):
        '''Initialize the data publisher.

Parameters
----------
datafeed : callable
    datafeed function.
        '''
        super( BacktestDataPublisher, self ).__init__()

        # initialize the subscriber dict
        self.subscribers = {}
        # next identifier for the subscriber
        self.nextId = 1
        # datafeed function
        self.datafeed = datafeed


    def connect( self, startDate=dt.date( 2012, 1, 1 ), endDate=dt.date.today() ):
        '''Put this Datafeed engine online and listened to the data change.

For the backtest engine, we extract all data for monitored securities and feed them
to the subscribers.

Parameters
----------
startDate : datetime.date
    start date of the backtesting;
endDate : datetime.date
    end date of the backtesting.
        '''
        topics = set()
        fields = set()
        for _, s in self.subscribers.items():
            t = s.getSubscribedTopics()
            f = s.getSubscribedDataFields()
            topics.update( t )
            if not ( f is None or fields is None ):
                fields.update( f )
            else:
                fields = None

        logging.debug( 'Subscribe data for {ts:s} and {fs:s}.'.format(
                ts=', '.join( list( topics ) ),
                fs=', '.join( list( fields ) ) if fields is not None else 'ALL' ) )
        # use data API to get the data
        data = self.datafeed( topics, startDate=startDate, endDate=endDate )

        # make sure the history is replayed in order
        groupedData = data.groupby( 'tradeDate' )
        dates = sorted( groupedData.groups.keys() )
        for asOfDate in dates:
            ddf = groupedData.get_group( asOfDate )
            self.openMarket( asOfDate )
            for ts, subdf in ddf.groupby( 'timestamp' ):
                self.notifyAll( subdf )


    def addSubscriber( self, subscriber ):
        '''Add subscriber to this publisher.

Parameters
----------
subscriber : datafeed.subscriber.Subscriber
    Add subscriber to the data publisher.

Returns
-------
subscriberId : int
    Identifier of the subscriber.
        '''
        subId = self.nextId
        self.nextId += 1

        self.subscribers[ subId ] = subscriber

        return subId


    def removeSubscriber( self, subscriberId ):
        '''Drop a given subscriber from the publisher.

Parameters
----------
subscriberId : int
    Identifier of the subscriber.

Returns
-------
subscriber : datafeed.subscriber.Subscriber
    Dropped subscriber.

Exceptions
----------
raise Exception when error occurs.
        '''
        if subscriberId not in self.subscribers:
            raise Exception( 'Requested subscriber does not exist.' )
        else:
            subscriber = self.subscribers.pop( subscriberId, None )

            return subscriber


    def notify( self, subscriberId, data ):
        '''Notify one subscriber by the subscriber ID.

Parameters
----------
subscriberId : int
    Identifier of the subscriber;
data : pandas.DataFrame
    data in pandas.DataFrame feed to the subscriber.

Returns
-------
None.

Exceptions
----------
raise Exception when error occurs.
        '''
        if subscriberId in self.subscribers:
            self.subscribers[ subscriberId ].onData( data )
        else:
            raise Exception( 'Subscriber with ID {sid:d} does not exist.'.format(
                    sid=subscriberId ) )


    def openMarket( self, asOfDate ):
        '''Market open on the given trading date.

Parameters
----------
asOfDate : str
    Trading date in the format %Y%m%d.
        '''
        for _, s in self.subscribers.items():
            s.openMarket( asOfDate )


    def notifyAll( self, data ):
        '''Notify all subscribers with the given data.

Exceptions
----------
raise Exception when error occurs.
        '''
        if len( self.subscribers ) > 0:
            for _, s in self.subscribers.items():
                s.onData( data )


# TODO this is a temporary solution, productionise it when test done.
def getFuturesTimeseries( secIds, column='closePrice', liquidWinLen=10,
        liquidThres=500 ):
    '''Get futures time series with the given securities ID's.

Parameters
----------
secIds : list of str
    list of all securites names to read;
column : str
    column name to read.

Returns
-------
data : pandas.DataFrame
    data returned in pandas.DataFrame indexed by tradeDate with column names SecID's.
    '''
    series = []
    for i, secId in enumerate( secIds ):
        secData = futuresApi.getDailyData( secId )
        # fiter out illiquid traded contract
        if ( secData is not None ) and \
           ( secData.turnoverVol.iloc[ -liquidWinLen : ] > liquidThres ).all():
            secData = secData[ [ column, 'tradeDate' ] ].dropna()
            secSeries = pd.Series( list( secData[ column ] ),
                            index=list( secData.tradeDate ),
                            name=secId )
            if len( secSeries ) == 0:
                logging.warning( 'Empty data for {sid:s}'.format( sid=secId ) )
            else:
                series.append( secSeries )
        else:
            logging.warning( 'Illiquid contracts for {sid:s}'.format( sid=secId ) )
     
    return pd.DataFrame( series ).T
