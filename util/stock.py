'''This module includes utility functions related to stock operation.
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
import numpy as np

# third-party modules

# customized modules


def adjustPrice( position, cash, dividend10=0.0, right10=0, rightIssue10=0,
        rightIssuePrice=0 ):
    '''Calculate the ex-dividend, ex-right price of a stock. If rationed shares are needed, cash
should be able to cover the cost of the rationed shares. Otherwise, there will
be net loss.

Parameters
----------
position : int
    the position of a stock;
cash : float
    cash left or available, in case we need to buy rationed shares;
dividend10 : float
    dividend per 10 shares;
right10 : float
    ex-right per 10 shares;
rightIssue10 : float
    right issued shares per 10 shares;
rightIssuePrice : float
    right issued price.

Returns
-------
( newPosition, newCash ) : tuple of ( int, float )
    The new position after the dividend and the cash left after.
    '''
    if rightIssue10 > 0:
        x = 1

    if right10 > 0:
        x = 1

    unit = int( position / 10 )
    newCash = cash + dividend10 * unit
    newPosition = position + int( unit * right10 )

    rightIssueVolume = int( rightIssue10 * unit )
    if cash > rightIssueVolume * rightIssuePrice:
        newCash -= rightIssueVolume * rightIssuePrice
        newPosition += rightIssueVolume

    return ( newPosition, newCash )


def roundVolume( volume, lotSize=100 ):
    '''Round the trading volume to lots.

Parameters
----------
volume : int
    total volume to round;
lotSize : int
    volume lot size, by default, 100 shares per lot.

Returns
-------
lotShares : int
    rounded volumes.
    '''
    return int( volume / lotSize ) * lotSize


def getWindExchId( secId ):
    '''Get exchange identifier for the given securities.

Parameters
----------
secId : str
    Securities identifier in a normal string.

Returns
-------
exchId : str
    exchange identifier. The rules are as below

* 6XXXXX - Shanghai Stock Exchange;
* 0XXXXX - Shenzhen Stock Exchange;
* 3XXXXX - Shenzhen Stock Exchange;
* 2XXXXX - Shenzhen Stock Exchange.
    '''
    prefix = secId[ 0 ]

    return 'SH' if prefix == '6' else 'SZ'
