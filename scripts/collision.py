#!/usr/bin/env python

# Copyright (c) 2016, BRML
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import argparse
import datetime
import os
import rospkg

import rospy

from baxter_data_acquisition.misc import as_boolean
from baxter_data_acquisition.simulation import sim_or_real
from experiments.collision import Experiment


def main():
    """ (Manual) collision data acquisition with the baxter research robot.

    Moves one limb through configurations randomly selected from a pre-defined
    set of configurations. For each movement between two configurations there
    is a probability that a collision is sampled to be due at a randomly
    sampled part of the limb. In this case the operator is instructed to hit
    the robot in the desired location.
    One sample consists of a number of configurations; a data set consists of
    a number of samples.
    """
    arg_fmt = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=arg_fmt,
                                     description=main.__doc__)
    required = parser.add_argument_group('required arguments')
    required.add_argument('-l', '--limb', required=True,
                          choices=['left', 'right'],
                          help='The limb to record data from.')
    parser.add_argument('-n', '--number', required=False,
                        type=int, default=1,
                        help='The number of samples to record.')
    parser.add_argument('-c', '--collisions', required=False,
                        type=str, default='false', choices=['true', 'false'],
                        help='Whether there are collisions in the data.')
    parser.add_argument('-j', '--joints', required=False,
                        type=str, default='true', choices=['true', 'false'],
                        help='Whether joint data are to be recorded.')
    parser.add_argument('-i', '--images', required=False,
                        type=str, default='false', choices=['true', 'false'],
                        help='Whether images are to be recorded.')
    parser.add_argument('-o', '--outfile', required=False,
                        type=str, default='',
                        help='Recorded data filename (without extension).')
    args = parser.parse_args(rospy.myargv()[1:])

    ns = rospkg.RosPack().get_path('baxter_data_acquisition')
    datapath = os.path.join(ns, 'data')
    if not os.path.exists(datapath):
        os.makedirs(datapath)
    if len(args.outfile) == 0:
        now = datetime.datetime.now()
        outfile = now.strftime("%Y%m%d%H%M")
    else:
        outfile = args.outfile
    # move all recorded data into a corresponding sub-folder
    filepath = os.path.join(datapath, outfile)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    filename = os.path.join(filepath, outfile)

    print 'Initializing node ...'
    rospy.init_node('collision_data', anonymous=True)

    sim = sim_or_real()
    exp = Experiment(limb=args.limb, number=args.number,
                     collisions=as_boolean(args.collisions),
                     joints=as_boolean(args.joints),
                     images=as_boolean(args.images), sim=sim)
    rospy.on_shutdown(exp.clean_shutdown)
    exp.execute(filename)

    print '\nDone.'

if __name__ == '__main__':
    main()
