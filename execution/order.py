'''This module abstracts the concept of an order with order specific operations.
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

class Order( object ):
    '''An abstraction of orders.
    '''
    # order side
    BUY     = 1
    SELL    = -1
    UNKNOWN = 0

    # order type
    LIMIT_ORDER  = 0
    MARKET_ORDER = 1

    # order action
    OPEN  = 0
    CLOSE = 1
    CLOSE_TODAY = 2
    NO_ACTION   = -1

    def __init__( self, secId, side, volume, price, priceType=LIMIT_ORDER, offset=None ):
        '''Initialize an order object.

Parameters
----------
secId : str
    Securities identifier of the order;
side : int
    side of the order;
volume : int
    volume of the order;
price : float
    order price;
offset : int
    offset of the order.

Exceptions
----------
Raise Exception when not enough information given to the order.
        '''
        super( Order, self ).__init__()
        self.secId  = secId
        self.side   = side
        self.volume = volume
        self.price  = price

        # default arguments
        self.priceType = priceType
        self.offset    = offset


    @classmethod
    def negateSide( cls, side ):
        '''Negate the order side.

Parameters
----------
side : int
    Order side to negate

* BUY  : 1
* SELL : -2
* UNKNOWN : 0

Returns
-------
newSide : int
    new order side.

* BUY  : 1
* SELL : -2
* UNKNOWN : 0

Exceptions
----------
raise Exception when mal-formed side information given.
        '''
        if side == cls.BUY:
            newSide = cls.SELL
        elif side == cls.SELL:
            newSide = cls.BUY
        elif side == cls.UNKNOWN:
            newSide = cls.UNKNOWN
        else:
            raise Exception( 'Mal-formed side information.' )

        return newSide


    @classmethod
    def isActionTaken( cls, action ):
        '''Check whether any action is taken.

Parameters
----------
action : int
    Indicator of action type defined in this class.

Returns
-------
actionTaken : boolean
    A boolean indicating whether the action is taken.
        '''
        return action != cls.NO_ACTION


class OrderId( object ):
    '''Order identifier.
    '''

    def __init__( self, rawIdObject ):
        '''
        '''
        super( OrderId, self ).__init__()


class OrderStatus( object ):
    '''Status of the order.
    '''

    def __init__( self ):
        '''
        '''
        super( OrderStatus, self ).__init__()

class SimpleOrder( Order ):
    '''A simple implementation of the order object.
    '''

    # order direction constants
    BUY  = 1
    SELL = -1
    UNKNOWN = 0

    # order type
    MARKET_ORDER = 0
    LIMIT_ORDER  = 1

    def __init__( self, secId, side, volume, price,
            effectivePrice=None ):
        '''Initialize the simple order object.

Parameters
----------
secId : str
    Identifier of the security;
side : int
    side of the order;
volume : int
    number of the contract;
orderType : int
    order type, either market order or limit order;
price : double
    order price.

Exceptions
----------
raise Exception when limit order without price.
        '''
        super( SimpleOrder, self ).__init__( secId, side, volume, price )

        self.effectivePrice = effectivePrice


class SimpleOrderStatus( OrderStatus ):
    '''Simple order status objects.
    '''

    SUBMITTED = 0
    CANCELLED = 1
    EXECUTED  = 2

    def __init__( self, orderStatus=None, secId=None, executedPrice=None,
            commision=None, orderDirection=None, orderSize=None ):
        '''Initalize the order status object with the given status, price, commision,
direction, and size.
        '''
        super( SimpleOrderStatus, self ).__init__()
        # initialize
        self.orderStatus    = orderStatus
        self.secId          = secId
        self.executedPrice  = executedPrice
        self.commision      = commision
        self.orderDirection = orderDirection
        self.orderSize      = orderSize
