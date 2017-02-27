'''This file contains utility functions related to math calculation.
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
import numpy as np

# customized modules

def movingAverage( a, winLen ):
    '''Compute the moving average of the given array with the specified window size.

Parameters
----------
a : iterable of number
    An iterable of numbers whose moving average is about to calculate;
winLen : int
    Length of the given window.

Returns
-------
mvAvg : iterable of number
    An iterable of moving averages.
    '''
    mvAvg = np.cumsum( a, dtype=float )
    mvAvg[ winLen : ] = mvAvg[ winLen : ] - mvAvg[ : -winLen ]

    return mvAvg[ winLen - 1 : ] / winLen


def gcd( a, b ):
    '''Find the greatest common divisor of the given two integers.

Parameters
----------
a : int
    Positive integer a; 
b : int
    positive integer b.

Rerturns
--------
gcd : int
    greatest common divisor of the two given integers.
    '''
    if a > b:
        tmp = b
        b   = a
        a   = tmp

    # make sure a is no greater than b
    while b % a != 0:
        c = b % a
        b = a
        a = c

    return a


def reduceFraction( num, den ):
    '''Reduce a fraction less than 1 to be the irreducible form.

Parameters
----------
num : int
    Positive integer represents the numerator of the fraction;
den : int
    positive integer represents the denominator of the fraction.
    '''
    if num == 0:
        frac = ( num, den )
    else:
        divisor = gcd( num, den )

        frac = ( num // divisor, den // divisor )

    return frac
   

def getNearestFraction( f, limit = 10 ):
    '''Get the nearest approximation of f. Use the Farey sequence to approximate
the fraction.

See

https://en.wikipedia.org/wiki/Farey_sequence
http://stackoverflow.com/questions/4385580/finding-the-closest-integer-fraction-to-a-given-random-real

Parameters
----------
f : float
    positive float;
limit : int
    maximum denominator.

Returns
-------
( numerator, denominator ) : tuple of float
    a tuple of numerator and denominator of the fraction.
    '''
    numA = 0
    denA = 1
    numB = 1
    denB = 1

    if f < 1 - f:
        error = f
        frac  = ( numA, denA )
    else:
        error = 1 - f
        frac  = ( numB, denB )

    while error > 0:
        # while frac[ 1 ] < limit and error > 0:
        numC, denC = reduceFraction( numA + numB, denA + denB )
        apprF    = numC / denC
        newError = abs( apprF - f )

        if denC > limit:
            break

        if newError < error:
            error = newError
            frac  = ( numC, denC )

        # exit when denominator reaches 10
        if f > numA / denA and f < apprF:
            numB, denB = numC, denC
        elif f > apprF and f < numB / denB:
            numA, denA = numC, denC

    return frac


def correlate( s1, s2 ):
    '''Calculate the correlation coefficient of the given two series.
    
Parameters
----------
s1 : pandas.Series
    Time series 1;
s2 : pandas.Series
    Time series 2.
    
Returns
-------
coeff : float
    Correlation coefficient.
    '''
    meanS1 = s1.mean()
    meanS2 = s2.mean()
    
    varS1 = np.square( s1 - meanS1 ).sum()
    varS2 = np.square( s2 - meanS2 ).sum()
    corr  = ( ( s1 - meanS1 ) * ( s2 - meanS2 ) ).sum()
    
    return corr / np.sqrt( varS1 * varS2 )


def infinitesimal( val ):
    '''Zero infinitesimal number.

Parameters
----------
val : float
    infinitesimal number.

Returns
-------
adjVal : float
    0.0 if the abs( number ) is less than 1e-6, otherwise the number itself.
    '''
    return 0.0 if abs( val ) < 1e-6 else val
