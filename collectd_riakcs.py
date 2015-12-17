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

        # https://github.com/basho/basho_docs/blob/riakcs/2.1.0/source/languages/en/riakcs/cookbooks/Monitoring-and-Metrics.md
        # https://github.com/basho/riak_cs/wiki/%5BRFC%5D-Riak-CS-and-Stanchion-metrics-2.1
        metrics = [
            "service_get", # GET Service
            "bucket_put", # PUT, HEAD, DELETE Bucket
            "bucket_head", # PUT, HEAD, DELETE Bucket
            "bucket_delete", # PUT, HEAD, DELETE Bucket
            "bucket_acl_get", # PUT, GET Bucket ACL
            "bucket_acl_put", # PUT, GET Bucket ACL
            "bucket_policy_get", # PUT, GET, DELETE Bucket Policy
            "bucket_policy_put", # PUT, GET, DELETE Bucket Policy
            "bucket_policy_delete", # PUT, GET, DELETE Bucket Policy
            "bucket_location_get", # GET Bucket Location
            "list_uploads_get", # listing all multipart uploads
            "multiple_delete_post", # Delete Multiple Objects
            "list_objects_get", # listing all objects in a bucket, equally GET Bucket
            "object_get", # GET, PUT, DELETE, HEAD Objects
            "object_put", # GET, PUT, DELETE, HEAD Objects
            "object_delete", # GET, PUT, DELETE, HEAD Objects
            "object_put_copy", # PUT Copy Object
            "object_acl_get", # GET, PUT Object ACL
            "object_acl_put", # GET, PUT Object ACL
            "multipart_post", # Initiate a multipart upload
            "multipart_upload_put", # PUT Multipart Upload, putting a part of an object by copying from existing object
            "multipart_upload_post", # complete a multipart upload
            "multipart_upload_delete", # delete a part of a multipart upload
            "multipart_upload_get", # get a list of parts in a multipart upload
        ]

        # counter metrics
        self.counters = []
        for metric in metrics:
            for term in ["in", "out"]:
                self.counters.append("%s_%s_total" % (metric, term))

        # gauges metrics
        self.gauges = []
        for metric in metrics:
            for term in ["95", "99", "100", "mean", "median"]:
                self.gauges.append("%s_time_%s" % (metric, term))

    def process_data(self, data):
        counters = collectd.Values(type='counter')
        counters.plugin = 'riakcs'

        gauges = collectd.Values(type='gauge')
        gauges.plugin = 'riakcs'

        for name in self.counters:
            if name in data:
                counters.dispatch(values=[data[name]],
                                  type_instance="%s" % name)
            else:
                collectd.warning("riakcs plugin: counter %s not found!" % name)
        for name in self.gauges:
            if name in data:
                gauges.dispatch(values=[data[name]],
                                type_instance="%s" % name)
            else:
                collectd.warning("riakcs plugin: gauge %s not found!" % name)

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
