#!/usr/bin/env python

import sys
import os
import argparse
import datetime
import requests
import logging
from calendar import monthrange

log = logging.getLogger(__name__)


def get_months(start_str, end_str):
    dates = []
    s_tok = start_str.split("-")
    e_tok = end_str.split("-")
    s_year = int(s_tok[0])
    s_month = int(s_tok[1])
    e_year = int(e_tok[0])
    e_month = int(e_tok[1])

    month = s_month
    for year in range(s_year, e_year + 1):
        if year == s_year:
            for month in range(month, 12 + 1):
                if month < 10:
                    dates.append(str(year) + "-0" + str(month))
                else:
                    dates.append(str(year) + "-" + str(month))
        elif year == e_year:
            for month in range(1, e_month + 1):
                if month < 10:
                    dates.append(str(year) + "-0" + str(month))
                else:
                    dates.append(str(year) + "-" + str(month))
        else:
            for month in range(1, 12 + 1):
                if month < 10:
                    dates.append(str(year) + "-0" + str(month))
                else:
                    dates.append(str(year) + "-" + str(month))

    return dates


def get_endpoints(inp):
    endpoints = {}
    items = inp.split(",")
    for item in items:
        details = item.split(":")
        endpoints[details[0]] = {"service": details[1], "group": details[2]}

    return endpoints


def get_month_days(date_str):
    tok = date_str.split("-")
    year = int(tok[0])
    month = int(tok[1])
    (w, days) = monthrange(year, month)
    return days


def get_host_stats(host, service, group, api, token, report, dates):
    log.info("Retrieving stats for host:{0} running service: {1} in group: {2}".format(host, service, group))
    url = "https://{0}/api/v2/results/{1}/{2}/{3}/services/{4}/endpoints/{5}?start_time={6}T00:00:00Z&end_time={7}T23:59:59Z&granularity=monthly"
    end_days = get_month_days(dates[len(dates) - 1])
    group_type = get_report_group(api, token, report)
    start_str = dates[0] + "-01"
    end_str = dates[len(dates) - 1] + "-" + str(end_days)
    final_url = url.format(api, report, group_type, group, service, host, start_str, end_str)
    headers = {'Accept': 'application/json', 'x-api-key': token}
    r = requests.get(final_url, headers=headers)

    if r.status_code == 200:
        j = r.json()
        content = j["results"][0]["serviceflavors"][0]["endpoints"][0]["results"]

        a = []
        r = []
        up = []
        unk = []
        down = []
        z = 0
        for i in range(0, len(dates)):
            if z >= len(content):
                a.append(' ')
                r.append(' ')
                up.append(' ')
                unk.append(' ')
                down.append(' ')
                continue
            if content[z]["timestamp"] != dates[i]:
                a.append(' ')
                r.append(' ')
                up.append(' ')
                unk.append(' ')
                down.append(' ')
                continue
            a.append(float(content[z]["availability"]))
            r.append(float(content[z]["reliability"]))
            up.append(float(content[z]["uptime"]))
            unk.append(float(content[z]["unknown"]))
            down.append(float(content[z]["downtime"]))
            z = z + 1
        return {"a": a, "r": r, "up": up, "unk": unk, "down": down}


def get_all_stats(endpoints, api, token, report, dates):
    stats = {}
    for endpoint in endpoints:
        stats[endpoint] = get_host_stats(endpoint, endpoints[endpoint]["service"], endpoints[endpoint]["group"], api,
                                         token, report, dates)
    return stats


def get_report_group(api, token, report):
    url = "https://{0}/api/v2/reports".format(api)
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'x-api-key': token}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        content = r.json()
        data = content["data"]
        for datum in data:
            if datum["info"]["name"] == report:
                return datum["topology_schema"]["group"]["group"]["type"]


def output(items, stats, months):
    lines = ""
    month_header = ","
    ar_header = ","
    for month in months:
        month_header = month_header + str(month) + ",,,,,"
        ar_header = ar_header + "availability,reliability,uptime,unknown,sched. downtime,"
    lines = lines + month_header + "\n" + ar_header + "\n"

    for item in items:
        out_ln = output_line(item, stats)
        lines = lines + out_ln + "\n"
    return lines


def output_line(item, inpdata):
    out = []
    data = inpdata[item]
    for i in range(0, len(data["a"])):
        out.append(data["a"][i])
        out.append(data["r"][i])
        out.append(data["up"][i])
        out.append(data["unk"][i])
        out.append(data["down"][i])
    return item + ", " + str(out).strip('[]').replace("'", "")


def parse_csv(csv):
    endpoints = {}
    with open(csv) as f:
        content = f.readlines()
        for ln in content:
            tok = ln.strip().split(",")
            endpoints[tok[0]] = {'service': tok[1], 'group': tok[2]}
    return endpoints


def main(args=None):
    logging.basicConfig(level= logging.INFOa)
    if args.csv:
        endpoints = parse_csv(args.csv)
    elif args.input:
        endpoints = get_endpoints(args.input)
    else:
        log.error(
            "Argument Error!\n   Either set -i (cmd line list of host:service:group,host:service:group \n\n  - OR - \n\n   Set -c path to input csv file with lines: host,service,group")
        exit(-1)
    months = get_months(args.start, args.end)
    stats = get_all_stats(endpoints, args.api, args.token, args.report, months)
    txt = output(endpoints, stats, months)
    print(txt)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monthly A/R statistics for list of service endpoints")
    parser.add_argument(
        "-i", "--input", metavar="STRING", help="comma separated list of host:service:group,host:service:group",
        required=False,
        dest="input")
    parser.add_argument(
        "-c", "--csv", metavar="PATH", help="path to a csv file with lines host,service,group,",
        required=False,
        dest="csv")
    parser.add_argument(
        "-s", "--start", metavar="DATE(YYYY-MM)", help="start date", required=True, dest="start")
    parser.add_argument(
        "-e", "--end", metavar="DATE(YYYY-MM)", help="end date", required=True, dest="end")
    parser.add_argument(
        "-a", "--api", metavar="STRING", help="api endpoint to connect to", required=True, dest="api")
    parser.add_argument(
        "-t", "--token", metavar="STRING", help="access token", required=True, dest="token")
    parser.add_argument(
        "-r", "--report", metavar="STRING", help="report name", required=True, dest="report")

    # Pass the arguments to main method
    sys.exit(main(parser.parse_args()))
