# :mailbox_with_no_mail: h8mail  

[![travis](https://img.shields.io/travis/khast3x/h8mail.svg)](https://travis-ci.org/khast3x/h8mail)
> Email OSINT and password finder.  
> Use h8mail to find passwords through [different breach and reconnaissance services](#apis), or the infamous "Breach Compilation" torrent.  
> Early release, feedback and pull requests are welcomed :heart:

##  :tangerine: Features

*  :mag_right: Email pattern matching (reg exp), useful for all those raw HTML files
* :whale: Small and fast Alpine Dockerfile available
* :white_check_mark: CLI or Bulk file-reading for targeting
* :memo: Output to CSV file
*  :loop: Reverse DNS + Open Ports
* :cop:  CloudFlare rate throttling avoidance
  - Execution flow remains synchronous and throttled according to API  usage guidelines written by service providers
*  :fire: Query and group results from [different breach service](#apis) providers
*  :fire: Query a local copy of the "Breach Compilation"
*  :fire: Get related emails
* :rainbow: Delicious colors

#### Demos

######  :unlock: Out of the box

![1](/doc/h8mail1.gif)

###### :rocket: With API services

![2](/doc/h8mail2.gif)

###### :minidisc: With the BreachedCompilation torrent
![3](/doc/h8mail3.gif)

####  APIs

|       Service      |         Functions        |         Status        |
|:--------------|:-----------------------:|:---------------------:|
| [HaveIBeenPwned](https://haveibeenpwned.com/) |      Number of email breachs      |   :white_check_mark: |
| [Shodan](https://www.shodan.io/)         | Reverse DNS, Open ports |   :white_check_mark: |
|[Hunter.io](https://hunter.io/) - Public   |Number of related emails   | :white_check_mark:  |
|[Hunter.io](https://hunter.io/) - Service (free tier)   |Cleartext related emails   | :white_check_mark:   |
|  [WeLeakInfo](https://weleakinfo.com/) - Public | Number of search-able breach results  |   :customs: |
|[WeLeakInfo](https://weleakinfo.com/) - Service   |Cleartext passwords, hashs and salts   |  :soon:  |
|[Snusbase](https://snusbase.com/) - Service   |Cleartext passwords, hashs and salts - Fast :zap:    | :white_check_mark:  |


## :tangerine: Install

If you're using Docker, make sure to add your `targets.txt` and your API keys in the configuration file **before** building
####  Local env
NodeJS is required to ensure CloudFlare bypassing. You can find out how to install it for your distribution [here](https://nodejs.org/en/download/package-manager/)

```bash
apt-get install nodejs
git clone https://github.com/khast3x/h8mail.git
cd h8mail
pip install -r requirements.txt
python h8mail.py -h
```

#### Docker

```bash
git clone https://github.com/khast3x/h8mail.git
cd h8mail
docker build -t h8mail .
docker run -ti h8mail -h
```

##  :tangerine: Usage

```bash
> python h8mail.py --help
usage: h8mail.py [-h] -t TARGET_EMAILS [-c CONFIG_FILE] [-o OUTPUT_FILE]
                 [-bc BC_PATH] [-v] [-l] [-k CLI_APIKEYS]

Email information and password finding tool

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET_EMAILS, --targets TARGET_EMAILS
                        Either single email, or file (one email per line).
                        REGEXP
  -c CONFIG_FILE, --config CONFIG_FILE
                        Configuration file for API keys
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        File to write output
  -bc BC_PATH, --breachcomp BC_PATH
                        Path to the breachcompilation Torrent.
                        https://ghostbin.com/paste/2cbdn
  -v, --verbose         Show debug information
  -l, --local           Run local actions only
  -k CLI_APIKEYS, --apikey CLI_APIKEYS
                        Pass config options. Format is "K:V,K:V"

```

## :tangerine: Usage examples

###### Query for a single target

```bash
python h8mail.py -t target@example.com
```

###### Query for list of targets, indicate config file for API keys, output to `pwned_targets.csv`
```bash
python h8mail.py -t targets.txt -c config.ini -o pwned_targets.csv
```

###### Query a list of targets against local copy of the Breach Compilation, pass API keys for [Snusbase](https://snusbase.com/) from the command line
```bash
python h8mail.py -t targets.txt -bc ../Downloads/BreachCompilation/ -k "snusbase_url:$snusbase_url,snusbase_token:$snusbase_token"
```

###### Query without making API calls against local copy of the Breach Compilation
```bash
python h8mail.py -t targets.txt -bc ../Downloads/BreachCompilation/ --local
```

## :tangerine: Troubleshooting

### Python version and Older Kali systems

The above instructions assume you are running python3 as default. If unsure, type:
```bash
python --version
``` 

in your terminal. It should be either `Python 3.*` or `Python 2.*`.  

If you are running python2 as default :  
Make sure you have python3 installed, then replace python commands with explicit python3 calls:

```bash
apt-get install nodejs
git clone https://github.com/khast3x/h8mail.git
cd h8mail
pip3 install -r requirements.txt
python3 h8mail.py -h
```



## :tangerine: Notes

* Service providers that wish being integrated can send me an email at `k at khast3x dot club` (Protonmail encryption friendly)
* Special thanks to [Snusbase](https://snusbase.com/) for being developer friendly
