#!/usr/bin/env python3

# This script is used to get the status of all monitors from uptime-kuma and output it in check_mk format
# The output is used in check_mk to monitor the uptime-kuma monitors
#
# To installin check_mk_agent:
# The Script can be installed on any host running the check_mk_agent
#
# apt install python3-dotenv python3-pip
# pip install uptime-kuma-api --break-system-packages


# Copy (or link) this script to /usr/lib/check_mk_agent/local/status_group.py
#  ln -sf /opt/src/kuma-create-checks/checkmk_status_plugin.py /usr/lib/check_mk_agent/local/uptime_kuma_stylite.py
# Create a .env_uptime_kuma_stylite.py file in the same directory 
# with the following content:
#
# BASE_URL=https://up.stylite.io
# CHECK_MK_HOST=kuma-ext
# CHECK_MK_PREFIX="Kuma-Ext "
# API_KEY=uk_xxxxxxxxxxxxxxxxxxx
# # Optional WARN and CRIT in ms for response time (default 100ms and 200ms, can be overwritten by (999ms) in the monitor name)
# WARN=677
# CRIT=1277
 
import os
import json
from dotenv import load_dotenv
from uptime_kuma_api import UptimeKumaApi, MonitorType
import requests
import re


# Read a env file with the name of this script 
dotenv_path = f".env_{os.path.basename(__file__)}"
if os.path.isfile(dotenv_path):
  load_dotenv(dotenv_path=dotenv_path)
#else:
  # We continue without the .env file

base_url = os.getenv("BASE_URL")
if base_url is None:
  print("No BASE_URL given")
  exit(1)

api_key = os.getenv("API_KEY")
if api_key is None:
  print("No API_KEY given")
  exit(1)

check_mk_host = os.getenv("CHECK_MK_HOST", "")
check_mk_prefix = os.getenv("CHECK_MK_PREFIX", "")
warn_default = int(os.getenv("WARN", 100))
crit_default = int(os.getenv("CRIT", 200))

# curl -u":uk3_xxxxxxxxx" https://up.stylite.io/metrics
#print(f"Base URL: {base_url}")
#print(f"API Key: {api_key}")

url = f"{base_url}/metrics"
response = requests.get(
  url,
  auth=("", api_key)
)
response.raise_for_status()

# The input is:
# HELP monitor_cert_days_remaining The number of days remaining until the certificate expires
# monitor_cert_days_remaining{monitor_name="Websites - Stylite",monitor_type="keyword",monitor_url="https://www.stylite.de/",monitor_hostname="null",monitor_port="null"} 55


# We want this output:
# <<<local:sep(0)>>>
#0 "stylite:stylite.de-http" response_time=0.037;1;3 OK: 37 ms, url https://stylite.de, type http
#0 "stylite:stylite.de-http-responsetime" load_time=37;688;1288|response_time=0.037 OK: 37 ms, url https://stylite.de, type http
#0 "stylite:stylite.de-http-cert" days_remaining=55;27;14 OK: url https://stylite.de, cert is valid 55 days days_remaining

my_response_time = {}
my_response_status = {}
my_response_cert = {}
my_response_cert_days = {}
my_response_hostname = {}
my_response_url = {}
my_response_type = {}
for line in response.text.split("\n"):
  line = line.strip()
  #print(line)
  pattern = r'(monitor_.*){monitor_name="([^"]+)",monitor_type="([^"]+)",monitor_url="([^"]+)",monitor_hostname="([^"]*)",monitor_port="([^"]*)"} (\d+)'
  matches = re.findall(pattern, line)

  if matches:
    monitor_check = matches[0][0]
    monitor_name = matches[0][1]
    monitor_type = matches[0][2]
    monitor_url = matches[0][3]
    monitor_hostname = matches[0][4]
    monitor_port = matches[0][5]
    monitor_result = matches[0][6]

    #print(f"Monitor Check: {monitor_check},")
    #print(f"Monitor Name: {monitor_name},")
    #print(f"Monitor Type: {monitor_type},")
    #print(f"Monitor URL: {monitor_url},")
    #print(f"Monitor Hostname: {monitor_hostname},")
    #print(f"Monitor Port: {monitor_port},")
    #print(f"Monitor Result: {monitor_result},")

    my_response_hostname[f"{monitor_name}-{monitor_type}"] = monitor_hostname
    my_response_url[f"{monitor_name}-{monitor_type}"] = monitor_url
    my_response_type[f"{monitor_name}-{monitor_type}"] = monitor_type
    if monitor_check == "monitor_response_time":
      my_response_time[f"{monitor_name}-{monitor_type}"] = monitor_result
    if monitor_check == "monitor_status":
      my_response_status[f"{monitor_name}-{monitor_type}"] = monitor_result
    if monitor_check == "monitor_cert_is_valid":
      my_response_cert[f"{monitor_name}-{monitor_type}"] = monitor_result
    if monitor_check == "monitor_cert_days_remaining":
      my_response_cert_days[f"{monitor_name}-{monitor_type}"] = monitor_result
    
# <<<< Says its piggyback for the host up-xxxxx
if check_mk_host != "":
  print(f"<<<<{check_mk_host}>>>>")
# Local:sep(0) is the separator
print("<<<local:sep(0)>>>")
for key in my_response_status:

  my_response_status1=3
  if key in my_response_status:
    my_response_status1 = my_response_status[key]

  status = 0
  my_status = my_response_status1

  my_response_time1=999
  my_response_time_seconds="9.999"
  if key in my_response_time:
    my_response_time1 = my_response_time[key]
    try:
      my_response_time1 = int(my_response_time1)
      my_response_time2 = my_response_time1/1000
      my_response_time_seconds = "{:.3f}".format(my_response_time2)
    except:
      my_response_time1 = 999
      my_response_time_seconds = "9.999"

  
  my_response_cert1="unk"
  my_response_cert2=0
  if key in my_response_cert:
    my_response_cert2 = my_response_cert[key]
    if my_response_cert2 == "1":
      my_response_cert1 = "valid"
    else:
      my_response_cert1 = "INVALID"
      
  my_response_url1="null"
  if key in my_response_url:
    my_response_url1 = my_response_url[key]

  my_response_hostname1="null"
  if key in my_response_hostname:
    my_response_hostname1 = my_response_hostname[key]

  my_response_type1="null"
  if key in my_response_type:
    my_response_type1 = my_response_type[key]

  if my_response_type1 == "group":
    # Skip groups in output
    continue

  my_response_cert_days1=0
  if key in my_response_cert_days:
    my_response_cert_days1 = int(my_response_cert_days[key])
  else:
    # No Cert check, so we set it to 999
    my_response_cert_days1 = 999

  # Clean key from UTF-8
  #key = key.encode('ascii', 'replace').decode('ascii')
  warn = warn_default
  crit = crit_default

  # search for pattern (100ms) in key and hostname
  pattern = r'\((\d+)ms\)'
  matches = re.findall(pattern, key+my_response_hostname1)
  if matches:
    warn = int(matches[0])
    crit = warn * 2
    # remove the pattern from the key to make it clean
    pattern = r'\s*\(\d+ms\)'
    key = re.sub(pattern, '', key).strip()

  if my_status == "1":    # 1 = UP
    status = 0              # check_mk status 0 = OK
  elif my_status == "0":  # 0 = DOWN
    status = 2              # check_mk status 2 = CRITICAL
  elif my_status == "2":   # 2 = PENDING
    status = 1              #  check_mk status 1 = WARN
  elif my_status == "3": # 3 = MAINTENANCE
    status = 3              # check_mk status 3 = UNKNOWN
  friendly_name = key
  if check_mk_prefix != "":
    friendly_name = f"{check_mk_prefix}{key}"

  print(f"{status} \"{friendly_name}\" response_time={my_response_time_seconds};1;3 OK: {my_response_time1} ms, url {my_response_url1}, type {my_response_type1}")


  status = 0
  if my_response_time1 > warn:
    status = 1
  elif my_response_time1 > crit:
    status = 2
  status_txt = f"load_time={my_response_time1};{warn};{crit}|response_time={my_response_time_seconds}"
  
  if my_response_type1 != "group":
    if warn > 0:
      print(f"{status} \"{friendly_name}-responsetime\" {status_txt} OK: {my_response_time1} ms, url {my_response_url1}, type {my_response_type1}")
  
  status = 0
  if my_response_cert1 != "unk":
    status = 1
    if my_response_cert_days1 > 27:
      status = 0
    elif my_response_cert_days1 < 14:
      status = 2
    if my_response_cert1 == "INVALID":
      status = 2
    print(f"{status} \"{friendly_name}-cert\" days_remaining={my_response_cert_days1};27;14 OK: url {my_response_url1}, cert is {my_response_cert1} {my_response_cert_days1} days remaining")

# Switch to the original host
if check_mk_host != "":
  # We need to switch back to the original host
  print(f"<<<<>>>>")
exit(0)