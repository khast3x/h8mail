# :mailbox_with_no_mail: h8mail - Alpha Release

> Email OSINT and password breach hunting.  
> Use h8mail to find passwords through different breach and reconnaissance services, or the infamous Breached Compilation!

##  :tangerine: Features

*  :mag_right: Email pattern matching (reg exp), useful for all those raw HTML files
* :whale: Small and fast Alpine Dockerfile available
* :white_check_mark: CLI or Bulk file-reading targeting
* :memo: Output to CSV file
*  :loop: Reverse DNS
* :cop:  CloudFlare rate throttling avoidance
  - Execution flow remains synchronous and throttled according to API  usage guidelines written by service providers
*  :fire: Query and group results from different breach service providers
*  :fire: Query a local copy of the "Breached Compilation"
*  :fire: Get related emails
*  :fire: Get target domain name open ports
* :rainbow: Delicious colors



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

```bash
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
                 [-bc BC_PATH] [-v]

Email information and breach notification tool

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET_EMAILS, --targets TARGET_EMAILS
                        Either single email, or file (one email per line).
                        REGEXP
  -c CONFIG_FILE, --config CONFIG_FILE
                        Configuration file for API keys
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        File to write output
  -bc BC_PATH, --breachedcomp BC_PATH
                        Path to the Breach Compilation Torrent.
                        https://ghostbin.com/paste/2cbdn
  -v, --verbose         Show debug information


```

## :tangerine: Examples

###### Query for a single target

```bash
python h8mail.py -t target@example.com
```

###### Query for list of targets, indicate config file for API keys, output to `pwned_targets.csv`
```bash
python h8mail.py -t targets.txt -c config.ini -o pwned_targets.csv
```

###### Query a list of targets against local copy of the Breach Compilation
```bash
python h8mail.py -t targets.txt -bc ../Downloads/BreachCompilation/
```

## :camera: Screenshot

![sc](https://i.imgur.com/i5o0RPP.png)


## :tangerine: Notes

* Service providers that wish being integrated can shoot me an email at `k at khast3x dot club` (Protonmail encryption friendly)
* Special thanks to [Snusbase](https://snusbase.com/) for being developer friendly
