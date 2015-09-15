collectd-riakcs
=============

A plugin for collectd to gather metrics for a `RiakCS <http://docs.basho.com/riakcs/latest/>`_
instance. Uses requests-aws module to get stats from Riak CS
`stats endpoint <http://docs.basho.com/riakcs/latest/cookbooks/Monitoring-and-Metrics/>`_,
then parses stats JSON.
