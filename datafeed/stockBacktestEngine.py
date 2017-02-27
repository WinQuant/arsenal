'''A data feed engine for stock backtesting.
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
import pandas as pd

# customized modules
import data.api.stocks as stockApi
import datafeed.engine as dEngine

# customized logging configure
logging.basicConfig( format='[%(levelname)s] %(message)s', level=logging.DEBUG )

class StockBacktestDataPublisher( dEngine.DataPublisher ):
    '''Data publish engine for stock backtesting.
    '''

    def __init__( self, dataSource ):
        '''Initialize the data publisher.

Parameters
----------
dataSource : data.api.stocks.DataSource
    Stock data source.
        '''
        self.dataSource = dataSource
        # next identifier for the subscriber
        self.nextId = 1
        # initialize the subscriber dict
        self.subscribers = {}


    def connect( self, startDate='20120101', endDate=dt.date.today().strftime( '%Y%m%d' ) ):
        '''Put the DataFeed engine online and listened to the data change.

For backtest engine, we extract all data for monitored securities and feed them
to the subscribers.

Parameters
----------
startDate : datetime.date
    start date of the backtesting;
endDate : datetime.date
    end date of the backtesting.
        '''
        # get all business dates
        businessDates = self.dataSource.getBusinessDates( startDate=startDate,
                endDate=endDate )

        for asOfDate in businessDates:
            print( 'Processing', asOfDate )
            self.notifyAll( asOfDate )


    def addSubscriber( self, subscriber ):
        '''Add subscriber to the publisher.

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
            self.subscribers[ subscriberId ].datafeed( data )
        else:
            raise Exception( 'Subscriber with ID {sid:d} does not exist.'.format(
                    sid=subscriberId ) )


    def notifyAll( self, data ):
        '''Notify all subscribers with the given data.

Exceptions
----------
raise Exception when error occurs.
        '''
        if len( self.subscribers ) > 0:
            for s in self.subscribers.values():
                s.datafeed( data )
