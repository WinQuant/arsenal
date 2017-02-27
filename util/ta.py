'''Technical analysis module.
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
import pandas as pd

# customized modules
import util.timeseries as ut

def rsi( ts, n ):
    '''Calculate the RSI indicator of the given time series with the given data.

Parameters
----------
ts : pandas.Series
    Time series data in pandas Series;
n : int
    number of points look backwards.

Returns
-------
rsi : float
    RSI indicator.
    '''
    D = pd.Series( 0, index=ts.index )
    U = pd.Series( 0, index=ts.index )

    closeDiff = ts.diff()
    D[ closeDiff < 0 ] = -closeDiff[ closeDiff < 0 ]
    U[ closeDiff > 0 ] = closeDiff[ closeDiff > 0 ]

    alpha = 1 - 1 / n
    ewmaU = ut.ewma( U, alpha )
    ewmaD = ut.ewma( D, alpha )

    # The offset 1 is used in case both ewmaU and ewmaD are 0's.
    return 100 * ewmaU / ( ewmaU + ewmaD + 1 )
