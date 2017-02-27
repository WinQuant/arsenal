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

import execution.order as order
import strats.base     as stratsBase

class SimpleCTA( stratsBase.Strategy ):
    '''Simple CTA buy when price above a threshold, sell when below.
    '''

    def __init__( self, instId, upperThres, lowerThres ):
        '''Initialize the simple strategy.

Parameters
----------
instId : str
    Instrument identifier;
upperThres : float
    upper threshold;
lowerThres : float
    lower threshold.
        '''
        self.instId     = instId
        self.upperThres = upperThres
        self.lowerThres = lowerThres


    # Subscriber interface
    def onData( self, data ):
        '''Get notification from the publisher.

Parameters
----------
data : pandas.DataFrame
    Message from publisher in pandas.DataFrame indexed by instrument identifier.

Exceptions
----------
raise Exception when error occurs.
        '''
        orders = []
        price  = data.ix[ self.instId ].price

        if price > self.upperThres:
            side   = order.Order.BUY
            offset = order.Order.OPEN
            volume = 1

            orders.append( order.Order( self.instId, side, volume, price,
                    priceType=order.Order.LIMIT_ORDER, offset=offset ) )
        elif price < self.lowerThres:
            side   = order.Order.SELL
            offset = order.Order.CLOSE
            volume = 1

            orders.append( order.Order( self.instId, side, volume, price,
                    priceType=order.Order.LIMIT_ORDER, offset=offset ) )

        return orders


    def getSubscribedTopics( self ):
        '''Topics / instruments to subscribe.

Returns
-------
topics : list of str
    [ self.instId ]
        '''
        return [ self.instId ]


    def isActive( self ):
        '''Check whether the given strategy is active or not.

Returns
-------
isActive : bool
    A flag indicating whether the given strategy is active in use or not.
        '''
        return True
