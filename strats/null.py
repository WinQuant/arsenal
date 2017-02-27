'''Null strategy for framework testing.
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
import strats.base as strats

# customize logging configure
logging.basicConfig( format='[%(levelname)s] %(message)s', level=logging.INFO )

class NullStrategy( strats.Strategy ):
    '''Null strategy for testing purpose.
    '''

    def __init__( self ):
        '''Initialize an empty strategy.
        '''
        super( NullStrategy, self ).__init__()


    def onData( self, datafeed ):
        '''Simply echo the data received by the strategy.

Paramters
---------
datafeed : pandas.DataFrame
    Datafeed from data engine indexed by securities identifider. the Datatime
    must exist.

Exceptions
----------
raise Exception when error occurs.
        '''
        logging.info( datafeed )

        return []


    def getSubscribedTopics( self ):
        '''Subscribe the daily data for IC1605 and IF1605.

Returns
-------
topics : list of str
    List of securities ID's concerned.
        '''
        return [ 'IC1605.CCFX', 'IF1605.CCFX' ]


    def getSubscribedDataFields( self ):
        '''Subscribe all data fields.

Returns
-------
fields : None
    All fields are tracked.
        '''
        return None