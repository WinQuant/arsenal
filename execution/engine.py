'''This interface defines the engine part of the execution module.
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

# customized modules

class ExecutionEngine( object ):
    '''An abstraction of the execution interface to communicate with outside
world.
    '''

    BUY  = 1
    SELL = -1

    def placeOrder( self, order, onOrderFilled=None ):
        '''Place the order through the given brokage.

Parameters
----------
order : execution.order.Order
    The order to place.

Returns
-------
orderId : object
    Identifier of the order;
onOrderFilled : callable
    the callback if given, when the submitted order is filled.

Exceptions
----------
raise Exception if error occurs when placing the order.
        '''

    def cancelOrder( self, orderId ):
        '''Cancel the plancement of an order.

Parameters
----------
orderId : object
    Identifier of the order to cancel.

Returns
-------
confirm : object
    An indicator whether the order is successfully canceled.

Exceptions
----------
raise Exception when error occurs.
        '''

    def queryStatus( self, orderId ):
        '''Check the status of a placed order.

Parameters
----------
orderId : object
    Identifier of the order to query.

Returns
-------
status : object
    Order status.

Exceptions
----------
raise Exception when error occurs.
        '''

    def updateOrder( self, orderId, newOrder ):
        '''Update the old one with the new one.

Parameters
----------
orderId : object
    Identifier of the order to update;
newOrder : execution.order.Order
    New order to place.

Returns
-------
orderId : object
    The identifier of the updated order.

Exceptions
----------
raise Exception when error occurs.
        '''

    def setCallbacks( self, onRspUserLogin=None, onOrderSubmitted=None,
            onOrderActionTaken=None, onOrderReturn=None, onTradeReturn=None ):
        '''Set callback functions for later processing.

Parameters
----------
onRspUserLogin : callable
    Callback function to response user login, None by default;
onOrderSubmitted : callable
    Callback function to response order submit, None by default;
onOrderActionTaken : callable
    Callback function to acknowledge order action taken, None by default;
onOrderReturn : callable
    Callback function to response order return, None by default;
onTradeReturn : callable
    Callback function to response trade return, None by default;
        '''
