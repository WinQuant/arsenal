'''An execution engine for backtesting.
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
import execution.engine as eEngine
import execution.order  as order

# initialize logging configure
logging.basicConfig( format='[%(levelname)s] %(message)s', level=logging.INFO )

class BacktestExecutionEngine( eEngine.ExecutionEngine ):
    '''An execution engine for backtesting.

Each time an order is placed, it is executed immediately. The problem needs to
tackle is that we don't have an accounting unit. It is implemented internally.
    '''

    def __init__( self, commisionRate, marketImpact, refData ):
        '''Initialize the backtest engine.

Parameters
----------
commision : double
    commision rate;
marketImpact : int
    number of ticks for the market impact;
refData : execution.refData.RefData
    reference data related to the backtesting, including tick size, etc.
        '''
        self.commisionRate = commisionRate
        self.marketImpact  = marketImpact
        self.refData       = refData

        self.executedOrders = {}

        # next order identifier
        self.nextId = 1

    def placeOrder( self, order, onOrderFilled ):
        '''Place the order as a backtest engine.

Parameters
----------
order : execution.order.SimpleOrder
    Order to do the backtest;
onOrderFilled : callable
    Callable with one order object

Returns
-------
orderId : int
    Identifier of the order.
        '''
        orderId = self.nextId
        self.nextId += 1
        self.executedOrders[ orderId ] = order

        orderStatus = self.queryOrder( orderId )
        onOrderFilled( orderStatus )

        return orderId


    def cancelOrder( self, orderId ):
        '''Cancel the given order.
For backtesting, once placed, the order is executed.

Parameters
----------
orderId : int
    Identifier of the order.

Returns
-------
orderStatus : execution.order.SimpleOrderStatus
    Status of the backtest order, typically, failed to cancel, since the order is
    executed once placed.
        '''
        return order.SimpleOrderStatus( orderStatus=order.SimpleOrderStatus.EXECUTED )


    def updateOrder( self, orderId, order ):
        '''Update the given order with the specified order ID.

Parameters
----------
orderId : int
    Identifier of the order;
order : execution.order.SimpleOrder
    Newly updated order.

Returns
-------
newOrderId : int
    newly updated order identifier.
        '''
        return -1


    def queryOrder( self, orderId ):
        '''Get information about the order.

Parameters
----------
orderId : int
    Identifier of the order.

Returns
-------
orderStatus : execution.order.SimpleOrderStatus
    Status of the backtest order, including executed price,
    commision, order direction, order size, etc.

Exceptions
----------
If the requested order is not recognized, raise Exception.
        '''
        if orderId not in self.executedOrders:
            raise Exception( 'Given order {oid:d} does not exist.'.format(
                    oid=orderId ) )
        else:
            orderObj = self.executedOrders[ orderId ]

            secId     = orderObj.secId
            direction = 1 if orderObj.side == order.SimpleOrder.BUY else -1
            price     = orderObj.price
            size      = orderObj.volume

            tickSize  = self.refData.getTickSize( orderObj.secId )

            effectivePrice = price + \
                             direction * tickSize * self.marketImpact

            # commision
            contractFactor = self.refData.getLotSize( orderObj.secId )
            commision      = effectivePrice * size * contractFactor * self.commisionRate
           

            orderStatus = order.SimpleOrderStatus(
                    orderStatus=order.SimpleOrderStatus.EXECUTED,
                    secId=secId, executedPrice=effectivePrice,
                    commision=commision, orderDirection=direction,
                    orderSize=size )

            return orderStatus
