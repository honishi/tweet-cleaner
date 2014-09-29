tweet cleaner
==
time based tweet cleaner.

setup
--
````
pyenv install 3.4.1
pyenv virtualenv 3.4.1 tweet-cleaner-3.4.1
pip install -r requirements.txt
````
````
cp clean.configuration.sample clean.configuration
vi clean.configuration
````

start & stop
--
````
./clean.sh start
./clean.sh stop
````

monitoring example using cron
--
see `clean.sh` inside for details of monitoring.
````
* * * * * /path/to/tweet-cleaner/clean.sh monitor >> /path/to/tweet-cleaner/log/monitor.log 2>&1
````

license
--
MIT License.
copyright (c) 2013 honishi, hiroyuki onishi
