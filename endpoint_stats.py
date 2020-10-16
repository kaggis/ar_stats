#!/usr/bin/env python

from calendar import monthrange
from datetime import datetime, date, timedelta
import requests
import sys
import os
import argparse

import logging

log = logging.getLogger("endpoint_stats")


def get_endpoints(api,report,key,dt):
    url = "https://{0}/api/v2/results/{1}/endpoints?start_time={2}T00:00:00Z&end_time={2}T23:59:59Z"
    headers = {"Accept":"application/json", "x-api-key": key}
    r_url = url.format(api,report,dt)
    r = requests.get(r_url, headers=headers)
    return r.json()

def diff_dates(start_date, end_date): 
    dd = {} 
    d1 = datetime.strptime(start_date,"%Y-%m") 
    d2 = datetime.strptime(end_date,"%Y-%m") 
    d2_num_days = monthrange(d2.year, d2.month)[1] 
    sdate = date(d1.year, d1.month, 1)   # start date 
    edate = date(d2.year, d2.month, d2_num_days)   # end date 
    
    delta = edate - sdate       # as timedelta 
    m = 0 
    prefix = "" 
    for i in range(delta.days + 1): 
        day = sdate + timedelta(days=i) 
        if day.month is not m: 
            prefix = day.strftime("%Y-%m") 
            m = day.month 
            dd[prefix] = [] 
        dd[prefix].append(str(day)) 
         
         
    return dd 

def get_report(api,report,key,dates):
    r_endp = set()
  
    for day in dates:
        log.info(" ...for day: " + day)
        z = get_endpoints(api,report,key,day)
        if "results" not in z:
            continue
        for item in z["results"]:
            r_endp.add(item["name"] + "_" + item["service"])
            
    return r_endp

def get_reports_per_month(api,reports,key,dates):
    sum = 0
    for report in reports:
        log.info("accessing api:" + api + " report: "+ report)
        r = get_report(api,report,key,dates)
        sum = sum + len(r)
    return sum


def main(args=None):
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    results = []
    dd = diff_dates(args.start, args.end)

    reports = args.reports.split(",")

    for month in dd:
        num = get_reports_per_month(args.api,reports,args.key,dd[month])
        results.append((month,num))
    
    # print csv output
    print("month,endpoints")
    for r in results:
        print(r[0]+","+str(r[1]))




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Calculate unique endpoints per tenant")
    parser.add_argument(
        "-r", "--reports", metavar="STRING", help="Report/s in a comma separated list of values", required=True, dest="reports")
    parser.add_argument(
        "-s", "--start-date", metavar="DATE(YYYY-MM)", help="Start date in YYYY-MM format", required=True, dest="start")
    parser.add_argument(
        "-e", "--end-date", metavar="DATE(YYYY-MM)", help="End date in month format", required=True, dest="end")
    parser.add_argument(
        "-k", "--api-key", metavar="STRING", help="Api access key", dest="key")
    parser.add_argument(
        "-a", "--api-endpoint", metavar="STRING", help="Api endpoint url", dest="api")
    parser.add_argument("-v", help="verbose",
                        dest="verbose", action="store_true")

    # Pass the arguments to main method
    sys.exit(main(parser.parse_args()))
