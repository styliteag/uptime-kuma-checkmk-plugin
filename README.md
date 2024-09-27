# Install

The Script can be installed on any host running the check_mk_agent.

## Prerequisites

Install the required packages:

```
apt install python3-dotenv python3-setuptools python3-pip
pip install uptime-kuma-api --break-system-packages
```

Copy (or link) this script to /usr/lib/check_mk_agent/local/status_group.py

```
ln -sf /opt/src/kuma-create-checks/checkmk_status_plugin.py /usr/lib/check_mk_agent/local/uptime_kuma_stylite.py
```

Create a .env_uptime_kuma_stylite.py file in the same directory 
with the following content:

```
# Put this in the .env file
BASE_URL=https://your-uptime.kuma.url
API_KEY=uk_xxxxxxxxxxxxxxxxxxx
# Optional Hostname (piggyback)
# CHECK_MK_HOST=kuma-ext
# Optional Prefix (e.g. "Kuma-Ext ")
# CHECK_MK_PREFIX="Kuma-Ext "
# # Optional WARN and CRIT in ms for response time (default 100ms and 200ms, can be overwritten by (999ms) in the monitor name)
# WARN=677
# CRIT=1277
```
