'''An interface of the data subscriber-publisher pattern.
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

class Publisher( object ):
    '''
    '''
    def addSubscriber( self, subscriber ):
        '''Add subscriber to this data feed source.

Parameters
----------
subscriber : datafeed.subpub.Subscriber
    Add subscriber to the publisher for later notification.

Returns
-------
subscriberId : object
    Identifier of the subscriber.

Exceptions
----------
raise Exception when error occurs.
        '''

    def removeSubscriber( self, subscriberId ):
        '''Drop a given subscriber from the publisher.

Parameters
----------
subscriberId : object
    Identifier of the subscriber.

Returns
-------
confirm : object
    Confirmation of the success of the subscription.

Exceptions
----------
raise Exception when errors occur.
        '''

    def notify( self, subscriberId, data ):
        '''Notify one subscriber by the subscriber ID.

Parameters
----------
subscriberId : object
    Identifier of the subscriber;
data : object
    raw data for the internal system.

Exceptions
----------
raise Exception when error occurs.
        '''

    def notifyAll( self, data ):
        '''Notify all subscribers.

Parameters
----------
data : object
    raw data.

Exceptions
----------
raise Exception when error occurs.
        '''

class Subscriber( object ):
    '''An abstraction of the subscriber objects.

Exceptions
----------
raise Exception when errors occur.
    '''

    def onData( self, data ):
        '''Get notification from the publisher.

Parameters
----------
data : pandas.DataFrame
    Messages from publisher in pandas.DataFrame.

Exceptions
----------
raise Exception when error occurs.
        '''


    def getSubscribedTopics( self ):
        '''Topics to subscribe.

Returns
-------
topics : list of str
    A list of topics to subscribe.
        '''
        return [ '' ]


    def getSubscribedDataFields( self ):
        '''Data fields to subscribe.

Returns
-------
subscribedFields : list of str or None
    List of str representing the fields to subscribe, if None returned,
subscribe all data fields.

Notes
-----
The following fields are accepted case insensitive.
* VOLUME
* PRICE
* BID
* ASK
* RT_VOLUME
* RT_PRICE
* etc.
        '''
