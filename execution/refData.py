'''Reference data abstract for backtesting.
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

# customized modules
import data.api.futures as futuresApi

# customize logging configure
logging.basicConfig( format='[%(levelname)s] %(message)s', level=logging.INFO )

WIND_DATE_FORMAT   = '%Y%m%d'
WIND_DEFAULT_START_DATE = '20120101'

class RefData( object ):
    '''Reference data.
    '''

    def getTickSize( self, secId, asOfDate=None ):
        '''Tick size of the security.

Paramters
---------
secId : str
    name of the security;
asOfDate : str
    data date of the margin ratio in the format '%Y%m%d'.

Returns
-------
tickSize : float
    size of a tick for the given instrument.
        '''
        return 0.01

    def getLotSize( self, secId, asOfDate=None ):
        '''Lot size of the security.

Parameters
----------
secId : str
    name of the security;
asOfDate : str
    data date of the margin ratio in the format '%Y%m%d'.

Returns
-------
lotSize : int
    number of shares/contracts in a lot.
        '''
        return 1

    def getMarginRate( self, secId, asOfDate=None ):
        '''Margin rate for the instrument.

Parameters
----------
secId : str
    name of the security;
asOfDate : str
    data date of the margin ratio in the format '%Y%m%d'.

Returns
-------
marginRate : float
    Margin rate of the trade.
        '''
        return 1.0


    def getUpLimit( self, secId, asOfDate=None ):
        '''Get up limit of the given instrument.

Parameters
----------
secId : str
    name of the security;
asOfDate : str
    data date of the margin ratio in the format '%Y%m%d'.

Returns
-------
upLimit : float
    up limit of the given instrument in percentage.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        return 0.1


    def getDownLimit( self, secId, asOfDate=None ):
        '''Get down limit of the given instrument.

Parameters
----------
secId : str
    name of the security;
asOfDate : str
    data date of the margin ratio in the format '%Y%m%d'.

Returns
-------
downLimit : float
    down limit of the given instrument in percentage.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        return 0.1


class FuturesRefData( RefData ):
    '''Futures reference data.
    '''

    def __init__( self, asOfDate=dt.date.today() ):
        '''Initialize the reference data for futures as of the given date.

Parameters
----------
asOfDate : datetime.date
    Data date.
        '''
        super( FuturesRefData, self ).__init__()

        # get the futures information
        self.futuresInfo = futuresApi.getFuturesInformation( asOfDate, listed=False )


    def getTickSize( self, secId ):
        '''Tick size of the security.

Paramters
---------
secId : str
    name of the security.

Returns
-------
tickSize : float
    size of a tick for the given instrument.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        record = self._getRecord( secId )

        return record.minChgPriceNum


    def getLotSize( self, secId ):
        '''Lot size of the security.

Parameters
----------
secId : str
    name of the security.

Returns
-------
lotSize : int
    number of shares/contracts in a lot.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        record = self._getRecord( secId )

        return record.contMultNum


    def getMarginRate( self, secId ):
        '''Margin rate for the instrument.

Parameters
----------
secId : str
    name of the security.

Returns
-------
marginRate : float
    Margin rate of the trade.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        # record = self._getRecord( secId )

        # return record.
        return 0.1


    def getTradeCommisionNumber( self, secId ):
        '''Get trade commision number.

Parameters
----------
secId : str
    name of the security.

Returns
-------
tradeCommision : float
    commision rate/price of the trade, if greater than 0, commision price,
    otherwise, commision rate.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        record = self._getRecord( secId )

        return record.tradeCommiNum


    def getUpLimit( self, secId ):
        '''Get up limit of the given instrument.

Parameters
----------
secId : str
    name of the security.

Returns
-------
upLimit : float
    up limit of the given instrument.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        record = self._getRecord( secId )

        return record.limitUpNumber * 0.01


    def getDownLimit( self, secId ):
        '''Get down limit of the given instrument.

Parameters
----------
secId : str
    name of the security.

Returns
-------
downLimit : float
    down limit of the given instrument.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        record = self._getRecord( secId )

        return record.limitDownNum * 0.01


    def _getRecord( self, secId ):
        '''Get the record describing the given instrument.

Parameters
----------
secId : str
    Name of the instrument.

Returns
-------
record : pandas.Series
    If the record on the given name exists, return the extracted record.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        record = self.futuresInfo[ self.futuresInfo.secID == secId ]
        if len( record ) == 0:
            raise Exception( 'No record found for futures contract {fr:s}.'.format(
                    fr=secId ) )
        else:
            record = record.iloc[ 0 ]

            return record


class FuturesWindRefData( FuturesRefData ):
    '''Futures reference data from Wind.
    '''

    def __init__( self, dataSource,
            asOfDate=dt.date.today().strftime( WIND_DATE_FORMAT ) ):
        '''Initialize futures reference database based on Wind.

Parameters
----------
dataSource : data.api.futures.WindDataSource
    Data source backed by Wind to get futures fundamental data;
asOfDate : str
    data date in the format '%Y%m%d'.
        '''
        self.dataSource  = dataSource

        self.futuresInfo = self.dataSource.getFuturesInfo()
        self.marginInfo  = self.dataSource.getMarginInfo( endDate=asOfDate )
        self.upDownLimit = self.dataSource.getUpDownLimit( endDate=asOfDate )
        self.commisionRate = futuresApi.getFuturesInformation( asOfDate, listed=False )


    def getTickSize( self, secId, asOfDate=None ):
        '''Tick size of the security.

Paramters
---------
secId : str
    Name of the security;
asOfDate : str
    data date of the margin ratio in the format '%Y%m%d'.

Returns
-------
tickSize : float
    size of a tick for the given instrument.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        record = self._getRecord( self.futuresInfo, secId )

        return record.S_INFO_MFPRICE


    def getLotSize( self, secId, asOfDate=None ):
        '''Lot size of the security.

Parameters
----------
secId : str
    Name of the security;
asOfDate : str
    data date of the lot size in the format '%Y%m%d'.

Returns
-------
lotSize : int
    number of shares/contracts in a lot.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        record = self._getRecord( self.futuresInfo, secId )

        return record.S_INFO_PUNIT


    def getMarginRate( self, secId, asOfDate ):
        '''Margin rate for the instrument.

Parameters
----------
secId : str
    Name of the security;
asOfDate : str
    data date of the margin ratio.

Returns
-------
marginRate : float
    Margin rate of the trade.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        record = self._getRecord( self.marginInfo, secId, asOfDate=asOfDate )

        return record.MARGINRATIO


    def getTradeCommisionNumber( self, secId, asOfDate ):
        '''Get trade commision number.

Parameters
----------
secId : str
    name of the security.

Returns
-------
tradeCommision : float
    commision rate/price of the trade, if greater than 0, commision price,
    otherwise, commision rate.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        record = self._getRecord( self.commisionRate, secId,
                asOfDate=asOfDate )

        return record.tradeCommiNum


    def getUpLimit( self, secId, asOfDate ):
        '''Get up limit of the given instrument.

Parameters
----------
secId : str
    name of the security.

Returns
-------
upLimit : float
    up limit of the given instrument.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        record = self._getRecord( self.upDownLimit, secId, asOfDate=asOfDate, dateColumn='CHANGE_DT' )

        return record.PCT_CHG_LIMIT / 100


    def getDownLimit( self, secId, asOfDate ):
        '''Get down limit of the given instrument.

Parameters
----------
secId : str
    name of the security.

Returns
-------
downLimit : float
    down limit of the given instrument.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        return self.getUpLimit( secId, asOfDate )


    def _getRecord( self, infoTable, secId, asOfDate=None, dateColumn='TRADE_DT' ):
        '''Get the record describing the given instrument.

Parameters
----------
infoTable : str
    Information table to extract the record;
secId : str
    name of the instrument, both name.exch and name formats are accepted;
asOfDate : str or None
    data date in the format '%Y%m%d'.

Returns
-------
record : pandas.Series
    If the record on the given name exists, return the extracted record.

Exceptions
----------
raise Exception when no records found on the given instrument name.
        '''
        instId = secId.split( '.' )[ 0 ]
        record = infoTable[ infoTable.S_INFO_WINDCODE == instId ]
        if asOfDate is not None:
            record = record[ record[ dateColumn ] <= asOfDate ]

        nData = len( record )
        if nData == 0:
            raise Exception( 'No record found for futures contract {fr:s}.'.format(
                    fr=secId ) )
        elif nData == 1:
            record = record.iloc[ 0 ]
        else:
            record.sort_values( dateColumn, inplace=True )
            record = record.iloc[ -1 ]

        return record
