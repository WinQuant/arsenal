'''Calendar for trading date management.
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

# customized modules

DEFAULT_TS_START_DATE = '20050101'

class TradingCalendar( object ):
    '''Trading calendar.
    '''

    def __init__( self, dataSource, startDate=DEFAULT_TS_START_DATE ):
        ''' Initialize a trading calendar with the given data source.

Parameters
----------
dataSource : data.api.stocks.DataSource
    Data source to get the trading date information;
startDate : str
    start date of the calendar in the format '%Y%m%d'.
        '''
        super( TradingCalendar, self ).__init__()

        self.dataSource = dataSource
        self.startDate  = startDate


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
        '''


    def nextTradingDate( self, asOfDate, n=1 ):
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
        '''


class AShareTradingCalendar( TradingCalendar ):
    '''Trading calendar in A-share stock market.
    '''

    def __init__( self, dataSource, startDate=DEFAULT_TS_START_DATE ):
        ''' Initialize a trading calendar with the given data source.

Parameters
----------
dataSource : data.api.stocks.DataSource
    Data source to get the trading date information;
startDate : str
    start date of the calendar in the format '%Y%m%d'.
        '''
        super( AShareTradingCalendar, self ).__init__( dataSource, startDate=startDate )

        self.tradingDates = self.dataSource.getBusinessDates( startDate=self.startDate )


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
        '''
        earlyDates = self.tradingDates[ self.tradingDates < asOfDate ]
        prevDate   = asOfDate
        if len( earlyDates ) > 0:
            prevDate = earlyDates.iloc[ -n ]
        else:
            raise Exception( 'Date {0:s} is too early to be backtested.'.format( asOfDate ) )

        return prevDate


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
        '''
        laterDates = self.tradingDates[ self.tradingDates >= sinceDate ]
        nextDate   = sinceDate
        if len( laterDates ) > 1:
            nextDate = laterDates.iloc[ n ]
        else:
            raise Exception( 'Date {0:s} is too early to be backtested.'.format( sinceDate ) )

        return nextDate


class CFuturesTradingCalendar( AShareTradingCalendar ):
    '''Trading calendar in Chinese Commodity futures market.
    '''

    def __init__( self, dataSource, startDate ):
        ''' Initialize a trading calendar with the given data source.

Parameters
----------
dataSource : data.api.futures.DataSource
    Data source to get the trading date information;
startDate : str
    start date of the calendar in the format '%Y%m%d'.
        '''
        super( CFuturesTradingCalendar, self ).__init__( dataSource, startDate )
