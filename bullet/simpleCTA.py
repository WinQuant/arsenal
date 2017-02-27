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

import bullet.core as core

import strats.CTA.simpleCTA as sc
import strats.portfolio as port

import ctp.ctpDataPublisher   as ctpdp
import ctp.ctpExecutionEngine as ctpee

CTP_CONFIG_FILE = 'ctp/config.yaml'

class SimpleCTABullet( core.Bullet ):
    def __init__( self ):
        super( SimpleCTABullet, self ).__init__( None, None, None )


    def run( self ):
        futuresRefData = refData.FuturesRefData()
        # execution engine
        trader = ctpee.CTPExecutionEngine( CTP_CONFIG_FILE )
        # data publisher
        datafeed = ctpdp.CTPDataPublisher( CTP_CONFIG_FILE )

        # construct the portfolio
        portfolio = port.Portfolio( trader )

        simpleCta = sc.SimpleCTA( 'CU1610.XSGE', 38000, 37000 )

        portfolio.addStrategy( simpleCta )

        # time to run
        datafeed.addSubscriber( portfolio )
        receiver = datafeed.connect()
        receiver.start()
        trader.connect()
        receiver.join()


if __name__ == '__main__':
    b = SimpleCTABullet()
    b.run()
