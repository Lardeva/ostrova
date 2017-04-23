export LD_LIBRARY_PATH="/usr/lib/oracle/12.1/client64/lib"
export ORACLE_HOME="/usr/lib/oracle/12.1/client64"
cd /home/osboxes/ostrovaweb
python3 manage.py runmodwsgi --reload-on-changes