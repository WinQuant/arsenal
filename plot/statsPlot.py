'''This module holds functions to plot the return curves.
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
import seaborn as sns
import matplotlib.pyplot as plt

# customized modules


def grossReturnRate( portfolioReturn, benchmarkReturn, figsize=( 12, 8 ), linewidth=1 ):
    '''Plot gross return rates compared with the benchmark.

Parameters
----------
portfolioReturn : pandas.Series
    A pandas series holding portfolio gross return;
benchmarkReturn : pandas.Series
    a pandas series holding benchmark return;
figsize : tuple
    figure size;
linewidth : int
    line width of the marker.
    '''
    if len( portfolioReturn ) == len( benchmarkReturn ):
        nData     = len( portfolioReturn )
        xTickStep = int( nData / 8 )
        rotation  = '30'

        _, ax = plt.subplots( figsize=figsize )
        ax.plot( range( nData ), portfolioReturn, label="Portfolio Return" )
        ax.plot( range( nData ), benchmarkReturn, label="Benchmark Return" )
     
        # labels and legends
        ax.set_ylabel( "Gross Return Rate" )

        ax.set_xticks( range( 0, nData, xTickStep ) )
        ax.set_xticklabels( portfolioReturn.index[ :: xTickStep ], rotation=rotation )
        axHandles, axLabels = ax.get_legend_handles_labels()
        ax.legend( axHandles, axLabels, loc=0 )
    else:
        raise Exception( 'Portfolio return and benchmark return should be in the same shape.' )
