## ar_stats.py: 
### Quickly gather a/r stats for service endpoints

This script can be used to quickly generate a CSV containing monthly a/r stats for a list of endpoints. Each endpoints should be accompanied by the service flavor it supports and also the endpoint group it belongs to 

You can have two kinds of inputs:
1) A cmdline argument  `-i host:service:group,host:service:group,...` (A comma separated list of different hosts. Each host item uses `:` to separate host, service and group sections
2) A CSV file containing lines in the following format: `host,service,group`. Include the csv file input using cmdline argument `-c /path/to/file.csv`

### Script execution and full parameters

- `-a`, `--api`: the domain name of the designated argo-web-api host 
- `-t`, `--token`: the access token to argo-web-api host
- `-r`, `--report`: the name of the report to get a/r results from 
- `-s`, `--start`: the month to start query - in the format `YYYY-MM`
- `-e`, `--end`: the month to end query - in the format `YYYY-MM`

- `-i`, `--input`: a comma separated list of `host:service:group,host:service:group`
- `-c`, `--csv`: a path to the csv file containing lines of `host,service,group`

For example, to gather a/r data from api endpoint `api.argo.foo` for the report `Critical` and using access-token `s3cret` for the span of the months `2018-11` till `2019-03` and having two hosts: 
- `host1` running `service1` in group `group1`
- `host2` running `service2` in group `group2`

and want to store it in the file `test_output.csv` we issue:

```
./ar_stats -i host1:service1:group1,host2:service2:group2 -a api.argo.foo -t s3cret -r Critical -s 2018-11 -e 2019-03 > test_output.csv
```

If the input is instead in the file `/path/to/input.csv` we issue 

```
./ar_stats -c /path/to/input.csv -a api.argo.foo -t s3cret -r Critical -s 2018-11 -e 2019-03 > test_output.csv
```


