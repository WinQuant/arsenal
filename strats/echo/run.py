'''This is a dummy implememtation of the strategy interface.

The strategy simply dumps market data to standard output.
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
from strats.base import Strategy

# customize logging configure
logging.basicConfig( format='[%(levelname)s] %(message)s', level=logging.INFO )

class EchoStrategy( Strategy ):
    '''Dummy echo strategy to test whether the CTP channel is ready.
    '''
    
    def __init__( self, secId ):
        '''Initialize the dummy strategy.
        '''
        super( EchoStrategy, self ).__init__()

        self.secId = secId


    # subscriber interface
    def onData( self, data ):
        '''Get notification from the subscriber.
        '''
        logging.info( data )

        # DO NOT place any orders
        return []


    def onOrderFilled( self, filledOrder ):
        '''The callback function for order fill notification.

Parameters
----------
filledOrder : execution.order.OrderStatus
    Filled order status.
        '''


    def getSubscribedTopics( self ):
        '''Topics / instruments to subscribe.

Returns
-------
topics : list of str
    [ self.secId ]
        '''
        return [ self.secId ]


    # Strategy interface
    def mtm( self, closeInfo ):
        '''Calculate mark-to-market with the closed price.

Parameters
----------
closeInfo : pandas.DataFrame
    Close information.

Returns
-------
mtm : float
    0.0
        '''
        return 0.0


    def isActive( self ):
        '''Check whether the given strategy is active or not.

Returns
-------
isActive : bool
    A flag indicating whether the given strategy is active in use or not.
        '''
        return True


    def getPnls( self ):
        '''Get PnL's of the strategy.

Returns
-------
pnls: pandas.Series
    Strategy PnL's in pandas Series.
        '''
        return pd.Series( [ 0.0 ] )


    def showResults( self ):
        '''Strategy related plotting. No operations in this case.
        '''
