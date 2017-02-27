'''Data feed engine for stock.
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
import pandas   as pd
import time

# third-party modules
import datafeed.stocks.PySubscribeApi as subscribe

# customized modules
import datafeed.engine as dEngine
import util.stock      as sUtil

# customize logging configure
logging.basicConfig( format='[%(levelname)s] %(message)s', level=logging.DEBUG )


class StockDataPublisher( subscribe.SubscribePythonSpi, dEngine.DataPublisher ):
    '''Data publisher for stocks.
    '''

    def __init__( self, configPath ):
        '''Initialize the stock data publisher.

Parameters
----------
configPath : str
    path to the configure for the data feed provided by the tech team.
        '''
        super( StockDataPublisher, self ).__init__()

        # initialize the subscriber dict
        self.subscribers = {}

        # mapping from instrument to concerned topics
        self.topicsToSubscribers = {}

        # next identifier for the subscriber
        self.nextId = 1

        # initialize the data publisher
        self.init( configPath )


    def connect( self, startDate=dt.date( 2012, 1, 1 ), endDate=dt.date.today() ):
        '''Put the data feed engine online and subscribe to the interested topics.

Parameters
----------
startDate : datetime.date
    start date filter;
endDate : datetime.date
    end date filter.
        '''
        super( StockDataPublisher, self ).connect()
        logging.info( 'Waiting connection to establish...' )


    def addSubscriber( self, subscriber ):
        '''Add subscriber to the publisher.

Parameters
----------
subscriber : datafeed.subpub.Subscriber
    Add subscriber to the data publisher.

Returns
-------
subscriberId : int
    Identifier of the subscriber.
        '''
        if subscriber is not None:
            subId = self.nextId
            self.nextId += 1

            self.subscribers[ subId ] = subscriber

            # add the subscriber to the topics to subscribers mapping
            subscribedTopics = subscriber.getSubscribedTopics()
            for topic in subscribedTopics:
                if topic not in self.topicsToSubscribers:
                    self.topicsToSubscribers[ topic ] = set()

                logging.debug( 'Add subscriber {sid:d} to topic {t:s}.'.format(
                        sid=subId, t=topic ) )
                self.topicsToSubscribers[ topic ].add( subscriber )
        else:
            subId = None

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

            if subscriber is not None:
                # drop the subscriber from the topic to subscribers mapping
                subscribedTopics = subscriber.getSubscribedTopics()
                for topic in subscribedTopics:
                    logging.debug( 'Remove subscriber {sid:d} from topic list {t:s}.'.format(
                            sid=subscriberId, t=topic ) )
                    self.topicsToSubscribers[ topic ] -= { subscriber, }


    def notify( self, subscriberId, data ):
        '''Notify one subscriber by the subscriber ID.

Parameters
----------
subscriberId : int
    Identifier of the subscriber;
data : pandas.DataFrame
    data in pandas.DataFrame feed to the subscriber.

Exceptions
----------
raise Exception when error occurs.
        '''
        if subscriberId in self.subscribers:
            self.subscribers[ subscriberId ].onData( data )
        else:
            raise Exception( 'Subscriber with ID {sid:d} does not exist.'.format(
                    sid=subscriberId ) )


    def notifyAll( self, data ):
        '''Notify all subscribers with the given data.

Parameters
----------
data : object
    data feed to all the subscribers.

Exceptions
----------
raise Exception when error occurs.
        '''
        # find all the subscribers that care about the datafeed.
        secIds = set( data.index )
        subscribers = set()
        for secId in secIds:
            subscribers = subscribers.union( self.topicsToSubscribers.get( secId, set() ) )

        if len( subscribers ) > 0:
            for s in subscribers:
                s.onData( data )


    # interfaces from SubscribePythonSpi
    def onRtnConnect( self, data ):
        '''Callback for stock datafeed connection.

Parameters
----------
data : dict
    connection status.
        '''
        if data[ 'statusCode' ] == 0:
            logging.info( 'Connection established.' )
            # login authentication
            self.login()
            logging.info( 'Waiting login to front...' )
        else:
            logging.warn( 'Fail to connect to front.' )


    def onRtnRspLogin( self, data ):
        '''Callback for stock datafeed login.

Parameters
----------
data : dict
    login status.
        '''
        if data[ 'statusCode' ] == 0:
            # summaries all the messages to subscribe
            topics = set()
            fields = set()
            for _, s in self.subscribers.items():
                t = s.getSubscribedTopics()
                f = s.getSubscribedDataFields()
     
                topics.update( t )
     
                if not ( f is None or fields is None ):
                    fields.update( f )
                else:
                    # if any subscriber subscribes all fields
                    # all fields are subscribed.
                    fields = None
     
            logging.info( 'Subscribe data for {ts:s} and {fs:s}.'.format(
                    ts=', '.join( list( topics ) ),
                    fs=', '.join( list( fields ) ) if fields is not None else 'ALL' ) )
     
            # add subscribed topics
            for secId in topics:
                exchId = sUtil.getWindExchId( secId )
                self.subscribe( 0, exchId, secId )
        else:
            logging.warn( 'Fail to login the data service.' )


    def OnRtnRspSubMarketData( self, data ):
        '''This is a must-have callback for receiving subscribe success notifying.

Parameters
----------
data : dict
    Data information.
        '''
        if data[ 'statusCode' ] == 0:
            # subscribe done
            logging.info( 'Subscribe done.' )
        else:
            msg = '{t:d} for {sid:s} on exchange {eid:s}.'.format(
                    t=data[ 'dataType' ], sid=data[ 'secID' ], eid=data[ 'exID' ] ) 
            logging.warn( 'Unable to subscribe {msg:s}'.format( msg=msg ) )


    def onPyRtnTransactionData( self, data ):
        '''Trade data return defined by SubscribePythonSpi.

Parameters
----------
data : dict
    latest trade data with the fields
* Seq         - message sequence number;
* ExID        - exchange identifier;
* SecID       - securities identifier;
* ExTime      - execution time in int hhmmssuuu;
* LocalTime   - local time when the trade executed(?);
* TradeTime   - official time when the trade executed;
* TradePrice  - the price where the order executed;
* Volume      - volume executed;
* Turnover    - monetary volume;
* TradeBuyNo  - buy side identifier;
* TradeSellNo - sell side identifier;
* TradeFlag   - trade identifier.
        '''
        # convert data from dict to DataFrame
        tradeTime = int( data[ 'TradeTime' ] / 1000 )
        tradeInfo = { 'secId': data[ 'SecID' ],
                      'tradeDate': dt.datetime.combine( dt.date.today(),
                            dt.time( int( tradeTime / 10000 ),
                                     int( tradeTime % 10000 / 100 ),
                                     int( tradeTime % 100 ) ) ),
                      'price': data[ 'TradePrice' ] / 10000 }

        tradeData = pd.DataFrame( tradeInfo, index=[ 0 ] )
        tradeData.set_index( 'secId', inplace=True )

        # notify subscribers about the data
        self.notifyAll( tradeData )
