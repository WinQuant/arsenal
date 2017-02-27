'''This class abstract the portfolio book.
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
import pandas as pd

# customized modules
import util.stock as stockUtil

# customize logging configure
logging.basicConfig( format='[%(levelname)s] %(message)s', level=logging.INFO )

class PortfolioPosition( object ):
    '''Trading book of a portfolio.
    '''

    def __init__( self, totalAsset ):
        '''Initialize the trading book.
        '''
        self.book = pd.DataFrame( columns=[ 'SecID', 'Price', 'Volume' ] )
        self.book.set_index( [ 'SecID' ], inplace=True )

        self.cash = totalAsset


    def getPositions( self ):
        '''Get current stock positions.

Parameters
----------
asOfDate : datetime.date
    Data date of the position to get.

Returns
-------
positions : pandas.DataFrame
    Positions hold in a pandas DataFrame with columns SecID, Price, and Volume.
        '''
        return self.book


    def getPosition( self, secId ):
        '''Get current stock position.

Parameters
----------
secId : str
    Name of the stock.

Returns
-------
position : int
    Position of the given securities.
        '''
        return self.book.ix[ secId ].Volume


    def getStocksInBook( self ):
        '''Get current stocks in the book.

Returns
-------
stocks : set of str
    All stocks in the book.
        '''
        return set( self.book.index )


    def isCashEnough( self, price, volume, commision ):
        '''Check whether the cash is enough to buy the instrument.

Parameters
----------
price : float
    Price to buy the instrument;
volume : int
    amount of instrument to buy;
commision : float
    commision fee to complete the trade.

Returns
-------
isEnough : bool
    An indicator whether the cash is enough.
        '''
        return self.cash > price * volume + commision


    def addPosition( self, secId, price, volume, commision ):
        '''Add one position.

Parameters
----------
secId : str
    Instrument identifier;
price : float
    execution price;
volume : int
    the amount of execution;
commision : float
    execution commision.
        '''
        position = self.getPositions()
        if secId in position.index:
            secPos = position.ix[ secId ]
            secPos.Price = ( secPos.Price * secPos.Volume + price * volume  ) / \
                    ( secPos.Volume + volume )
            secPos.Volume += volume
        else:
            position.ix[ secId ] = pd.Series( [ price, volume ], index=[ 'Price', 'Volume' ] )

        # need to spend cash to buy stock
        self.cash -= ( commision + price * volume )


    def deletePosition( self, secId, price, volume, commision ):
        '''Close a position.

Parameters
----------
secId : str
    Instrument identifier;
price : float
    execution price;
volume : int
    the amount of execution;
commision : float
    execution commision.
        '''
        position = self.getPositions()
        if secId in position.index:
            secPos = position.ix[ secId ]
            position.drop( secId, inplace=True )
            if volume > secPos.Volume:
                # We don't have enough holdings
                logging.warn( 'Expect to decrease the position on {secId:s} by {vol:d} at {p:f}, while only {hvol:d} available.'.format(
                        secId=secId, vol=int( volume ), p=price, hvol=int( secPos.Volume ) ) )
                availVol = secPos.Volume
            else:
                availVol = volume

            secPos.Volume -= availVol
            self.cash += availVol * price - commision

            if secPos.Volume > 0:
                # we still have positions, add back to the position
                position.ix[ secId ] = secPos


    def getTotalAsset( self, refPrices=None, excludeSuspended=None ):
        '''Get the total asset of the book with the given reference prices.

Parameters
----------
refPrices : pandas.DataFrame
    Reference prices of the holding instruments in pandas DataFrame.
If None, return current cash;
excludeSuspended : set of str
    All stocks suspended to be excluded when calculating total asset.

Returns
-------
totalAsset : float
    total asset.
        '''
        totalAsset = self.cash

        if refPrices is not None:
            # Let's clear-housing the position
            position        = self.getPositions()
            positionVolumes = position.Volume
            positionPrices  = refPrices[ refPrices.S_INFO_WINDCODE.isin(
                    position.index ) ].set_index(
                    [ 'S_INFO_WINDCODE' ] ).S_DQ_CLOSE
            monetaryVolumes = positionVolumes * positionPrices
            if excludeSuspended is None:
                totalAsset += monetaryVolumes.sum()
            else:
                tradingStocks = set( monetaryVolumes.index ) - excludeSuspended
                totalAsset += monetaryVolumes.ix[ list( tradingStocks ) ].sum()
                # totalAsset += monetaryVolumes[ ~monetaryVolumes.index.isin( tradingStocks ) ].sum()

        return totalAsset


    def adjustPrice( self, secId, dividend10=0, right10=0, rightIssue10=0, rightIssuePrice=0 ):
        '''Pay dividend of the given stock under the given plan.

Parameters
----------
secId : str
    Name of the stock;
dividend10 : float
    dividend per 10 shares;
right10 : int
    ex-stock right per 10 shares;
rightIssue10 : int
    rationed shares per 10 shares;
rightIssuePrice : float
    rationed prices.
        '''
        positions = self.getPositions()
        try:
            # the given instrument is under monitoring.
            secPos = positions.ix[ secId ]
            secPos.Volume, self.cash = stockUtil.adjustPrice( secPos.Volume,
                    self.cash, dividend10, right10, rightIssue10, rightIssuePrice )
        except KeyError:
            logging.warn( 'The given name {secId:s} is not in the portfolio book.'.format(
                    secId=secId ) )
