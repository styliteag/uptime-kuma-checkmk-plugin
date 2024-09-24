== Install ==

 
The Script can be installed on any host running the check_mk_agent

apt install python3-dotenv python3-setuptools python3-pip
pip install uptime-kuma-api --break-system-packages

Copy (or link) this script to /usr/lib/check_mk_agent/local/status_group.py
  ln -sf /opt/src/kuma-create-checks/checkmk_status_plugin.py /usr/lib/check_mk_agent/local/uptime_kuma_stylite.py

Create a .env_uptime_kuma_stylite.py file in the same directory 
with the following content:


BASE_URL=https://your-uptime.kuma.url

CHECK_MK_NAME=checkname

API_KEY=uk_xxxxxxxxxxxxxxxxxxx

WARN=677

CRIT=1277
