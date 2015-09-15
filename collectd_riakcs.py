#!/usr/bin/env python
# Collectd Riak-CS stats plugin
# ===
# This plugin needs requests-aws,
# install it with `pip install requests-aws`
#
# Copyright 2015 Alexander Bulimov <lazywolf0@gmail.com>
#
# Released under the MIT license, see LICENSE for details.
import collectd
import sys
import requests
import json
from awsauth import S3Auth

class RiakCSConfigException(Exception):
    pass

class RiakCS(object):
    def __init__(self):
        self.url = None
        self.access_key = None
        self.secret_key = None

    def process_data(self, data):
        # legend for meters: ["meter_count","meter_rate","latency_mean","latency_median","latency_95","latency_99"]
        # legend for pool: ["workers","overflow","size"]
        # explanation of this data see at
        # http://docs.basho.com/riakcs/latest/cookbooks/Monitoring-and-Metrics/

        counters = collectd.Values(type='counter')
        counters.plugin = 'riakcs'

        gauges = collectd.Values(type='gauge')
        gauges.plugin = 'riakcs'
        for name in data.keys():
            # we need only meters
            if len(data[name]) == 6:
                # meter_count
                counters.dispatch(values=[data[name][0]],
                                  type_instance="%s_count" % name)
                # meter_rate
                gauges.dispatch(values=[data[name][1]],
                                type_instance="%s_rate" % name)
                gauges.dispatch(values=[data[name][2]],
                                type_instance="%s_latency_mean" % name)
                gauges.dispatch(values=[data[name][3]],
                                type_instance="%s_latency_median" % name)
                gauges.dispatch(values=[data[name][4]],
                                type_instance="%s_latency_95th" % name)
                gauges.dispatch(values=[data[name][5]],
                                type_instance="%s_latency_99th" % name)

    def read_callback(self):
        try:
            auth = S3Auth(self.access_key, self.secret_key)
            r = requests.get(self.url, auth=auth)
            data = json.loads(r.text)
            self.process_data(data)
        except (requests.exceptions.RequestException, ValueError) as e:
            collectd.warning(e)

    def configure_callback(self,conf):
        for c in conf.children:
            if c.key == 'URL':
                self.url = c.values[0]
            elif c.key == 'AccessKey':
                self.access_key = c.values[0]
            elif c.key == 'SecretKey':
                self.secret_key = c.values[0]
            else:
                collectd.warning('riakcs plugin: Unknown config key: %s.' % c.key)
        if self.url is None:
            raise RiakCSConfigException('No URL specified')
        if self.access_key is None:
            raise RiakCSConfigException('No AccessKey specified')
        if self.secret_key is None:
            raise RiakCSConfigException('No SecretKey specified')

riak_cs = RiakCS()
collectd.register_config(riak_cs.configure_callback, name="riakcs")
collectd.register_read(riak_cs.read_callback, name="riakcs")
