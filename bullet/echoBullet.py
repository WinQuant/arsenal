# -*- coding: UTF-8 -*-
'''Market data repeater.
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

# customized modules
import bullet.core as core

import ctp.ctpDataPublisher   as ctpdp
import execution.backtestEngine as beEngine

import strats.echo.run  as echo
import strats.portfolio as port


# test CTP connection
CTP_CONFIG_FILE = 'ctp/config.yaml'

class EchoBullet( core.Bullet ):
    '''Simple bullet as a market repeater.
    '''

    def __init__( self ):
        '''Initialize the market echo portfolio bullet.
        '''
        super( EchoBullet, self ).__init__( None, None, None )


    def run( self ):
        '''Kick-off the run.
        '''
        # execution engine, which is a dummy one
        trader = beEngine.BacktestExecutionEngine( 0.0, 1, None )
        # data publisher
        datafeed = ctpdp.CTPDataPublisher( CTP_CONFIG_FILE )

        # construct the portfolio
        portfolio = port.Portfolio( trader )

        cu1608 = echo.EchoStrategy( 'CU1608.XSGE' )
        cu1609 = echo.EchoStrategy( 'CU1609.XSGE' )
        cu1610 = echo.EchoStrategy( 'CU1610.XSHG' )

        portfolio.addStrategy( cu1608 )
        portfolio.addStrategy( cu1609 )
        portfolio.addStrategy( cu1610 )

        datafeed.addSubscriber( portfolio )
        receiver = datafeed.connect()
        receiver.start()
        receiver.join()


if __name__ == '__main__':
    b = EchoBullet()
    b.run()
