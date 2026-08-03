# How to contribute to h8mail

*First of all, thank you for considering contributing :purple_heart:*  
*h8mail is very much a script turned into a tool. As such, the project is still evolving in regards to contribution guidelines.*  

*If this is your first contribution, I highly suggest you check [this repo](https://github.com/firstcontributions/first-contributions) first.*  

----


### The basics

* h8mail should only depend on the `requests` package

* Python 3.10 is the minimum supported version. User-visible CLI or output
  changes must update the [supported contract](docs/supported-contract.md) and
  its characterization tests.

* If adding a new feature or refactoring, consider opening an issue or sending me an email beforehand to ensure things go smoothly

* Comment your functions as docstrings

* Pull requests should be merged into the latest development branch, not in the main branch
  * If there is no on-going development branch, there should still be the current version's dev branch
  * If unsure, open an issue and you'll be pointed to the right branch, or a seperate branch can be created for you

* Make sure your code passes the included tests. Run the offline test suite with `python3 -m unittest` in h8mail's top-level directory. To include the opt-in live integration tests, use `RUN_INTEGRATION_TEST=1 python3 -m unittest tests.test_h8mail`.

* Pull requests targeting `master` and pushes to `master` run the offline test suite automatically across the Python versions in the GitHub Actions test matrix.

* Live integration tests run separately on a weekly schedule and can also be started manually from the GitHub Actions interface.

* Code should be formatted using [Python Black](https://github.com/psf/black). Most IDE's can run `black` directly. You can also launch it [from CLI](https://github.com/psf/black#installation-and-usage)

----

### Ways to contribute

* Bug reports using issues
* Bug fixes *(please open issues for typos)*
* Code refactoring *(please open issue beforehand if > 2 lines)*
* Code optimisation
* New features
* New API integrations

----

### Code of conduct

h8mail follows [Django's code of conduct](https://www.djangoproject.com/conduct/).
