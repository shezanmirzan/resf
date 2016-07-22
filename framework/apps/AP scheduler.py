"""
    Hello World message sender as example application 
    for the ResFi framework.

    Copyright (C) 2016 Sven Zehl, Anatolij Zubow, Michael Doering, Adam Wolisz

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    {zehl, zubow, wolisz, doering}@tkn.tu-berlin.de
"""

__author__ = 'zehl, zubow, wolisz, doering'

import time
from apscheduler.scheduler import Scheduler
from common.resfi_api import AbstractResFiApp
import numpy as np
import math
import Queue
import os
sched = Scheduler()
sched.start()                   #Start the scheduler

class ResFiApp(AbstractResFiApp):

    def __init__(self, log, agent):
        AbstractResFiApp.__init__(self, log, "de.berlin.tu.tkn.hello-world", agent)
    """
                Decoder.py
    """
                
        # Transferred to Agents.py (Class ResFI Agent ) 


    """
        Helper.py 

    """
        #Transfered to utils under the class ath9kSpectrumScanHelper

    """
        Scanner.py

    """
        #Transported to agent.py (Class ResFI Agent )

    def psd(self):
         # define scan params
        iface = 'wlan0'
        runt = 5
        ival = 0.05
        debug = False
        spectral_mode = 'background'    # 'background', 'manual'
        spectral_count = 8              # default=8
        spectral_period = 255           # default=255, max=255
        spectral_fft_period = 15        # default=15, max=15
        spectral_short_repeat = 1       # default=1 
        
        # configure scan device
        self.scan_dev_configure(
            iface=iface,
            mode=spectral_mode,
            count=spectral_count,
            period=spectral_period,
            fft_period=spectral_fft_period,
            short_repeat=spectral_short_repeat
            )
        # set timer
        start_time = time.time()
        end_time = start_time + runt

        # create plotter object
        #plt = psd_plotter.Plotter()

        # create scanner queue
        psdq = Queue.Queue()

        # start scan
        print("Start scanning PSD for %d sec in %d sec intervals on interface %s..." % (runt, ival, iface))
        if (spectral_mode == 'background'):
            self.scan_dev_start(iface)

        
        ival_cnt = 0
        while time.time() < end_time:

            if (spectral_mode == 'manual'):
                self.scan_dev_start(iface)

            # start scanner in a separate thread???
            self.scan(iface, psdq, debug)

            # collect all samples from last scan interval
            qsize = psdq.qsize()
            print("ival_cnt: %d, qsize: %d" % (ival_cnt, qsize))
            ret = np.full((56, qsize), (np.nan), dtype=np.float64)

            #while not myQueue.empty():
                #psd_pkt = myQueue.get()
                #print("Receiving PSD header: %s" % psd['header'])

            for i in range(0, qsize, 1):
                psd_pkt = psdq.get()
                ret[:,i] = psd_pkt['psd_vector']

            # calculate statistics for last scan interval
            avg = 10*np.log10(np.mean(10**np.divide(ret, 10), axis=1))
            #env = np.max(ret, axis=1)
            if(ival_cnt == 0):
                avgc = avg
            else:
                avgc = np.vstack((avgc,avg))
            print avgc.shape
            avgm = np.mean(avgc, axis = 0)

            if debug:
                print("Average power spectrum of last %d samples (%d sec):" % (qsize, ival))
                np.set_printoptions(formatter={'float': '{: 0.1f}'.format}, linewidth=120)
                print(avg)

                print("Envelope power spectrum of last %d samples (%d sec):" % (qsize, ival))
                np.set_printoptions(formatter={'float': '{: 0.1f}'.format}, linewidth=120)
                print(env)

            # update plotter
            #plt.updateplot(avg, env)

            # sleep for ival seconds
            ival_cnt += 1
            time.sleep(ival)

            self.log.debug("%s: plugin::hello-world started ... " % self.agent.getNodeID())

                    # send message to ResFi neighbors using ResFi northbound API
            my_msg = {}
            #my_msg['psd'] = {'qsize' : qsize, 'avg' : ival}
            
            #self.log.info("%s: plugin::hello-world sending %s to all one hop neighbors ... " 
                #% (self.agent.getNodeID(), str(my_msg)))
            #self.sendToNeighbors(my_msg, 1)
            
            time.sleep(1)

            self.log.debug("%s: plugin::hello-world stopped ... " % self.agent.getNodeID())




        #avg_cum = np.mean(avg, axis = 0)
        avgsend = {}
        for i in range(0,len(avgm),1):
            avgsend[i] = avgm[i]
        print str(avgsend)
        self.sendToNeighbors(avgsend, 1)
        #stop scan
        self.scan_dev_stop(iface)

    def run(self):
        self.log.debug("%s: plugin::spectralScan started ... " % self.agent.getNodeID())
        job = sched.add_interval_job(self.psd, minutes=1, start_date='2016-07-15 09:52:00')
                    


    """
    receive callback function
    """
    def rx_cb(self, json_data):
        self.log.info("%s :: recv() msg from %s at %d: %s" % (self.ns, json_data['originator'], 
            json_data['tx_time_mus'], json_data))

        message = json_data
        print message
        data = []
        for i in range (0,56,1):
            data.append(int(message.get(str(i))))
        for i in data:
            print i

    """
    new Link Notification Callback
    """
    def newLink_cb(self, nodeID):
        self.log.info("%s ::newLink_cb() new AP neighbor detected notification (newLink: %s)" 
            % (self.ns, nodeID))

    """
    Link Lost Notification Callback
    """
    def linkFailure_cb(self, nodeID):
        self.log.info("%s :: linkFailure_cb() neighbor AP disconnected (lostLink: %s)" 
            % (self.ns, nodeID))
