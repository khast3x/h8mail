 <p align="center">
<a href="https://github.com/khast3x/h8mail/releases/"> <img src="https://i.postimg.cc/LXR6Jq8Y/logo-transparent.png" width="420" title="h8maillogo">
</p>

[![platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux%20%7C%20OSX-success.svg)](https://pypi.org/project/h8mail/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/h8mail.svg)](https://pypi.org/project/h8mail/) [![Downloads](https://pepy.tech/badge/h8mail)](https://pepy.tech/project/h8mail)    [![travis](https://img.shields.io/travis/khast3x/h8mail.svg)](https://travis-ci.org/khast3x/h8mail)   
[![Docker Pulls](https://img.shields.io/docker/pulls/kh4st3x00/h8mail.svg)](https://hub.docker.com/r/kh4st3x00/h8mail) [![MicroBadger Size (tag)](https://img.shields.io/microbadger/image-size/kh4st3x00/h8mail.svg?color=ok)](https://hub.docker.com/r/kh4st3x00/h8mail/builds)  
> Powerful and user-friendly password hunting tool.  
> Use h8mail to find passwords through [different breach and reconnaissance services](#apis), or local breaches such as Troy Hunt's "Collection1" and the infamous "Breach Compilation" torrent.  
> First Anniversary update, feedback and pull requests are welcomed :heart: :birthday:

----
<p align="center">
<a href="https://khast3x.club/h8mail/2019/10/19/h8mail_2.4-release/?ref=readmebutton" First Anniversary update, feedback and pull requests are welcomed heart birthday"> <img src="https://i.postimg.cc/L83gRWvc/button-click-here-to-read-the-official-write-up.png"  title="h8maillogo">
</p>


----


## :book: Table of Content

- [Features](#tangerine-Features)
- [Demo](#Demo)
  - [Out of the box](#Out-of-the-box)
  - [With API services, local breach search & chasing enabled](#With-API-services-local-breach-search--chasing-enabled)
- [APIs](#APIs)
- [Install](#tangerine-Install)
- [Update](#Update)
- [Docker](#Docker)
- [Usage](#tangerine-Usage)
- [Configuration file & keys](#tangerine-Configuration-file--keys)
- [Supported custom queries](#tangerine-Supported-custom-queries)
- [Troubleshooting](#tangerine-Troubleshooting)
  - [Python version & Kali](#Python-version--Kali)
  - [Windows](#Windows)
  - [OSX](#OSX)
- [Thanks & Credits](#tangerine-Thanks--Credits)
- [Related open source projects](#tangerine-Related-open-source-projects)
- [Notes](#tangerine-Notes)
----


##  :tangerine: Features

* :mag_right: Email pattern matching (reg exp), useful for reading from other tool outputs
* :dizzy: Loosey patterns for local searchs ("john.smith", "evilcorp")
* :package: Painless install. Available through `pip`, only requires `requests`
* :white_check_mark: CLI or Bulk file-reading for targeting
* :memo: Output to CSV file
* :muscle: Compatible with the "Breach Compilation" torrent scripts
* :house: Search cleartext and compressed .gz files locally using multiprocessing
  * :cyclone: Compatible with "Collection#1"
* :fire: Get related emails
* :dragon_face: Chase related emails by adding them to the ongoing search
* :crown: Supports premium lookup services for advanced users
* :factory: Custom query premium APIs. Supports username, hash, ip, domain and password
* :books: Regroup breach results for all targets and methods
* :eyes: Includes option to hide passwords for demonstrations
* :rainbow: Delicious colors

---

### :package: `pip3 install h8mail`

-----

#### Demo

##### Out of the box
[![h8mail2demo6-1.gif](https://i.postimg.cc/DwbwqjwX/h8mail2demo6-1.gif)](https://postimg.cc/v4byyv9Y)


##### With API services & chasing enabled

[![pwoerchase2.gif](https://i.postimg.cc/3rn1K07Z/pwoerchase2.gif)](https://postimg.cc/qg6ywRNt)

##### Searching using username with API service, power chasing enabled

[![username.gif](https://i.postimg.cc/DZCj0BR7/username.gif)](https://postimg.cc/LY1B0BHW)

-----

####  APIs

| Service                                                        |                             Functions                             |           Status           |
|----------------------------------------------------------------|:-----------------------------------------------------------------:|:--------------------------:|
| [HaveIBeenPwned(v3)](https://haveibeenpwned.com/)              |                      Number of email breaches                     |  :white_check_mark: :key:  |
| [HaveIBeenPwned Pastes(v3)](https://haveibeenpwned.com/Pastes) |               URLs of text files mentioning targets               |  :white_check_mark: :key:  |
| [Hunter.io](https://hunter.io/) - Public                       |                      Number of related emails                     |     :white_check_mark:     |
| [Hunter.io](https://hunter.io/) - Service (free tier)          |                 Cleartext related emails, Chasing                 |  :white_check_mark: :key:  |
| [WeLeakInfo](https://weleakinfo.com/) - Public                 |                Number of search-able breach results               |  :white_check_mark: :key:  |
| [WeLeakInfo](https://weleakinfo.com/) - Service                |    Cleartext passwords, hashs and salts, usernames, IPs, domain   |  :white_check_mark: :key:  |
| [Snusbase](https://snusbase.com/) - Service                    | Cleartext passwords, hashs and salts, usernames, IPs - Fast :zap: |  :white_check_mark: :key:  |
| [Leak-Lookup](https://leak-lookup.com/) - Public               |                Number of search-able breach results               | :white_check_mark: (:key:) |
| [Leak-Lookup](https://leak-lookup.com/) - Service              |    Cleartext passwords, hashs and salts, usernames, IPs, domain   |  :white_check_mark: :key:  |
| [Emailrep.io](https://emailrep.io/) - Service (free)           |            Last seen in breaches, social media profiles           |     :white_check_mark:     |
| [Scylla.sh](https://scylla.sh/) - Service (free)               |  Cleartext passwords, hashs and salts, usernames, IPs, domain     | :white_check_mark:         |

*:key: - API key required*  


-----

## :tangerine: Install


### Requirements

h8mail 2.0 only requires the python `requests` module to run.

### Stable release (best)

**To install h8mail, run this command in your terminal:**  
```bash
$ pip3 install h8mail
```

**And that's basically it**.  
This is the preferred method to install h8mail, as it will always install the most recent stable release.

*Please note*:  
If you don't have [`pip`](https://pip.pypa.io) installed, this [Python installation guide](http://docs.python-guide.org/en/latest/starting/installation/) can guide
you through the process.  
For troubleshooting, check the [Troubleshooting](#tangerine-troubleshooting) section.

[![h8mail-install.gif](https://i.postimg.cc/Vs9vznN3/h8mail-install.gif)](https://postimg.cc/c6H0mKwm)
*The above illustration showcases installing h8mail using `--user`*



### From sources

The sources for h8mail can be downloaded from the [Github repo](https://github.com/khast3x/h8mail).

You can either clone the public repository:

```bash
$ git clone git://github.com/khast3x/h8mail
```
Or download the [tarball](https://github.com/khast3x/h8mail/tarball/master):

```bash
$ curl  -OL https://github.com/khast3x/h8mail/tarball/master
```
Next, decompress the downloaded archive.  
Once you have a copy of the source, you can install it with:

```bash
$ cd h8mail/
$ python setup.py install
$ h8mail -h
```

Or just running it as a module:
```bash
$ cd h8mail/
$ python -m h8mail -h
```

----

## Update

```bash
$ pip3 install --upgrade h8mail
```

Use `--user` at the end if getting a permission message from pip

----

## Docker

```bash
$ docker run -ti kh4st3x00/h8mail -h
```

-----

##  :tangerine: Usage

```bash
usage: h8mail [-h] [-t USER_TARGETS [USER_TARGETS ...]] [-q USER_QUERY]
              [--loose] [-c CONFIG_FILE [CONFIG_FILE ...]] [-o OUTPUT_FILE]
              [-bc BC_PATH] [-sk] [-k CLI_APIKEYS [CLI_APIKEYS ...]]
              [-lb LOCAL_BREACH_SRC [LOCAL_BREACH_SRC ...]]
              [-gz LOCAL_GZIP_SRC [LOCAL_GZIP_SRC ...]] [-sf]
              [-ch [CHASE_LIMIT]] [--power-chase] [--hide] [--debug]
              [--gen-config]

Email information and password lookup tool

optional arguments:
  -h, --help            show this help message and exit
  -t USER_TARGETS [USER_TARGETS ...], --targets USER_TARGETS [USER_TARGETS ...]
                        Either string inputs or files. Supports email pattern
                        matching from input or file, filepath globing and
                        multiple arguments
  -q USER_QUERY, --custom-query USER_QUERY
                        Perform a custom query. Supports username, password,
                        ip, hash, domain. Performs an implicit "loose" search
                        when searching locally
  --loose               Allow loose search by disabling email pattern
                        recognition. Use spaces as pattern seperators
  -c CONFIG_FILE [CONFIG_FILE ...], --config CONFIG_FILE [CONFIG_FILE ...]
                        Configuration file for API keys. Accepts keys from
                        Snusbase, WeLeakInfo, Leak-Lookup, HaveIBeenPwned and
                        hunterio
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        File to write CSV output
  -bc BC_PATH, --breachcomp BC_PATH
                        Path to the breachcompilation torrent folder. Uses the
                        query.sh script included in the torrent
  -sk, --skip-defaults  Skips HaveIBeenPwned and HunterIO check. Ideal for
                        local scans
  -k CLI_APIKEYS [CLI_APIKEYS ...], --apikey CLI_APIKEYS [CLI_APIKEYS ...]
                        Pass config options. Supported format: "K=V,K=V"
  -lb LOCAL_BREACH_SRC [LOCAL_BREACH_SRC ...], --local-breach LOCAL_BREACH_SRC [LOCAL_BREACH_SRC ...]
                        Local cleartext breaches to scan for targets. Uses
                        multiprocesses, one separate process per file, on
                        separate worker pool by arguments. Supports file or
                        folder as input, and filepath globing
  -gz LOCAL_GZIP_SRC [LOCAL_GZIP_SRC ...], --gzip LOCAL_GZIP_SRC [LOCAL_GZIP_SRC ...]
                        Local tar.gz (gzip) compressed breaches to scans for
                        targets. Uses multiprocesses, one separate process per
                        file. Supports file or folder as input, and filepath
                        globing. Looks for 'gz' in filename
  -sf, --single-file    If breach contains big cleartext or tar.gz files, set
                        this flag to view the progress bar. Disables
                        concurrent file searching for stability
  -ch [CHASE_LIMIT], --chase [CHASE_LIMIT]
                        Add related emails from hunter.io to ongoing target
                        list. Define number of emails per target to chase.
                        Requires hunter.io private API key
  --power-chase         Add related emails from ALL API services to ongoing
                        target list. Use with --chase. Requires a private API
                        key
  --hide                Only shows the first 4 characters of found passwords
                        to output. Ideal for demonstrations
  --debug               Print request debug information
  --gen-config, -g      Generates a configuration file template in the current
                        working directory & exits. Will overwrite existing
                        h8mail_config.ini file

```

-----

## :tangerine: Usage examples

###### Query for a single target

```bash
$ h8mail -t target@example.com
```

###### Query for list of targets, indicate config file for API keys, output to `pwned_targets.csv`
```bash
$ h8mail -t targets.txt -c config.ini -o pwned_targets.csv
```

###### Query a list of targets against local copy of the Breach Compilation, pass API keys for [Snusbase](https://snusbase.com/) from the command line
```bash
$ h8mail -t targets.txt -bc ../Downloads/BreachCompilation/ -k "snusbase_url=$snusbase_url,snusbase_token=$snusbase_token"
```

###### Query without making API calls against local copy of the Breach Compilation
```bash
$ h8mail -t targets.txt -bc ../Downloads/BreachCompilation/ -sk
```

###### Search every .gz file for targets found in targets.txt locally

```bash
$ h8mail -t targets.txt -gz /tmp/Collection1/ -sk
```

###### Check a cleartext dump for target. Add the next 10 related emails to targets to check. Read keys from CLI

```bash
$ h8mail -t admin@evilcorp.com -lb /tmp/4k_Combo.txt -ch 10 -k "hunterio=ABCDE123"
```
###### Query username. Read keys from CLI

```bash
$ h8mail -t JSmith89 -q username -k "weleakinfo_priv=ABCDE123"
```

###### Query IP. Chase all related targets. Read keys from CLI


```bash
$ h8mail -t 42.202.0.42 -q ip -c h8mail_config_priv.ini -ch 2 --power-chase
```

-----

## :tangerine: Configuration file & keys

h8mail can generate a template configuration file in the current working directory using `-g`.  
h8mail can read keys by using a `config.ini` file with `-c`, or by passing keys from the command line directly with `-k`.

*(links contain refs)*  
You can purchase API keys for:  
- [HaveIBeenPwned](https://haveibeenpwned.com/API/Key?ref=h8mail)  
- [hunter.io](https://hunter.io/users/sign_up?utm_medium=api?ref=h8mail)
- [Snusbase](https://snusbase.com/?ref=h8mail)
- [WeLeakInfo](https://weleakinfo.com/?ref=h8mail)
- [Leak-Lookup](https://leak-lookup.com/?ref=h8mail)


The configuration file format is as follows:
```ini
[h8mail]
hunterio =
hibp =
snusbase_url =
snusbase_token =
; leak-lookup_pub = 1bf94ff907f68d511de9a610a6ff9263
leak-lookup_priv =
weleakinfo_pub =
weleakinfo_priv =
```

In the above example, you'll notice a Leak-lookup public key, graciously generated for h8mail users. To activate, uncomment the line and make sure to pass to config file. The API can sometimes timeout. If that's the case, simply relaunch. 



Keys and their respective values can also be passed from the command line, with the `-k` option. Format is like so:  
```
$ h8mail -t john.smith@evilcorp.com -k "K=V, K=V" "K=V"
$ h8mail -t john.smith@evilcorp.com -k "leak-lookup_pub=1bf94ff907f68d511de9a610a6ff9263"
```

-----

## :tangerine: Supported custom queries

|            |      username      |       domain       |        hash        |      password      |         ip         |
|------------|:------------------:|:------------------:|:------------------:|:------------------:|:------------------:|
| WeLeakInfo | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| LeakLookup | :white_check_mark: | :white_check_mark: |                    | :white_check_mark: | :white_check_mark: |
| Snusbase   | :white_check_mark: |                    | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| Scylla.sh  | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |


As of writing, some service providers are undergoing upgrades and might support additional queries.  
To use a custom query, use `-q` followed by the appropriate keyword 


-----

## :tangerine: Troubleshooting



### Python version & Kali

* The above instructions assume you are running **python3 as default**. If unsure, type the following in your terminal.  
It should be either `Python 3.*` or `Python 2.*` :
```bash
$ python --version
``` 

* If you are running python2 as default :  
Make sure you have python3.6+ installed, then replace `python` commands with explicit `python3` commands.

* If you have not set your venvs, you might get a permission error saying `Consider using the --user option or check the permissions.`  
Simply add --user like so:
```bash
$ pip install --user h8mail
```

### Windows

* `h8mail` uses ANSI color escape characters. Windows doesn't know how to show the colors, and will show gibberish instead.  
Fortunately, you can use [Cmder](https://cmder.net/), which is an excellent Windows CMD prompt alternative
* If you're having trouble with python and pip, chances are you need to [add python to your PATH](https://geek-university.com/python/add-python-to-the-windows-path/). `pip` will also need to be in your `PATH` environment variable.
* If you're still having trouble with `pip`, you can do the following:
```bash
# Check python version, should be 3.6+
C:> python --version
# To have python handle installation of pip
C:> python -m ensurepip
# To launch pip as a module
C:> python -m pip install h8mail
# To launch h8mail as a module
C:> python -m h8mail --help
```

To find where `pip` installed h8mail, use `pip3 show h8mail`

### OSX

* As described for Windows, you might encounter issues with python if your installation is incomplete, or `pip`'s installation directory is not in your PATH.
* If thats the case, you can try invoking `pip` and `h8mail` with the same command lines as Windows.
* Make sure the `python` command refers to Python 3 with `python --version`, otherwise replace `python` with `python3` in the instructions.
* Basically try this if installed and not executing, check Windows instructions for further examples:
```bash
$ python3 -m h8mail -h
```  

-----

## :tangerine: Thanks & Credits

* [Snusbase](https://snusbase.com/) for being developer friendly
* [kodykinzie](https://twitter.com/kodykinzie) for making a nice [introduction and walkthrough article](https://null-byte.wonderhowto.com/how-to/exploit-recycled-credentials-with-h8mail-break-into-user-accounts-0188600/) and [video](https://www.youtube.com/watch?v=z8G_vBBHtfA) on installing and using h8mail
* [Leak-Lookup](https://leak-lookup.com/) for being developer friendly
* [WeLeakInfo](https://weleakinfo.com/) for being developer friendly  
* h8mail's Pypi integration is strongly based on the work of audreyr's [CookieCutter PyPackage](https://github.com/audreyr/cookiecutter-pypackage)
* Logo generated using Hatchful by Shopify
* [Jake Creps](https://twitter.com/jakecreps) for his [h8mail v2 introduction](https://jakecreps.com/2019/06/21/h8mail/)  
* [Alejandro Caceres](https://twitter.com/_hyp3ri0n) for making scylla.sh available. Be sure to [support](https://www.buymeacoffee.com/Eiw47ImnT) him if you can

-----

## :tangerine: Related open source projects
* [WhatBreach](https://github.com/Ekultek/WhatBreach) by Ekultek
* [HashBuster](https://github.com/s0md3v/Hash-Buster) by s0md3v
* [BaseQuery](https://github.com/g666gle/BaseQuery) by g666gle
* [LeakLooker](https://github.com/woj-ciech/LeakLooker) by woj-ciech
* [buster](https://github.com/sham00n/buster) by sham00n
* [Scavenger](https://github.com/rndinfosecguy/Scavenger) by ndinfosecguy
* [pwndb](https://github.com/davidtavarez/pwndb) by davidtavarez


-----

## :tangerine: Notes

* Service providers that wish being integrated can send me an email at `k at khast3x dot club` (PGP friendly)
* h8mail is maintained on my free time. Feedback and war stories are welcomed.
* Licence is BSD 3 clause
* My code is [signed](https://help.github.com/en/articles/signing-commits) with my [Keybase](https://keybase.io/ktx) PGP key. You can get it using:  
```bash
# curl + gpg pro tip: import ktx's keys
curl https://keybase.io/ktx/pgp_keys.asc | gpg --import

# the Keybase app can push to gpg keychain, too
keybase pgp pull ktx
```
___

*If you wish to stay updated on this project:*

<p align="center">
<a href="https://twitter.com/kh4st3x"> <img src="https://i.imgur.com/S79Nimd.png" width="420" title="h8maillogo">
</p>

