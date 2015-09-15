# collectd-riakcs

A plugin for [collectd](https://collectd.org/) to gather metrics
for a [RiakCS](http://docs.basho.com/riakcs/latest/)
instance. Uses [requests-aws](https://github.com/tax/python-requests-aws) module
to get stats from Riak CS
[stats endpoint](http://docs.basho.com/riakcs/latest/cookbooks/Monitoring-and-Metrics/),
then parses stats JSON.

## Setup

Using pip

```
pip install 'git+https://github.com/abulimov/collectd-riakcs#egg=collectd-riakcs'
```

## Configuration


```
LoadPlugin "python"

<Plugin python>
    Import "collectd_riakcs"

    <Module riakcs>
      SecretKey "RIAK_CS_SECRET_KEY"
      AccessKey "RIAK_CS_ACCESS_KEY"
      URL "http://127.0.0.1:8080/riak-cs/stats"
    </Module>
</Plugin>
```

## Contributing

Please read [CONTRIBUTING.md](https://github.com/abulimov/collectd-riakcs/blob/master/CONTRIBUTING.md) if you wish to contribute.

## License

(c) 2015 Alexander Bulimov.

Licensed under the [MIT License](http://opensource.org/licenses/MIT).
