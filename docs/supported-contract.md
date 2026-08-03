# Supported contract

This document defines the behavior that h8mail users and downstream automation
can rely on during modernization. Changes to this contract require an explicit
compatibility decision and corresponding test updates.

## Runtime support

- Python 3.10 is the minimum supported version.
- CPython 3.10 through 3.14 are exercised by continuous integration.
- h8mail is installed as the `h8mail` console command and can also be invoked
  with `python -m h8mail`.

## Command-line behavior

- `h8mail --help` prints usage information and exits successfully.
- Unknown options and malformed option values are rejected by `argparse` and
  exit with status 2.
- A normal search requires exactly one input mode:
  - `--targets` / `-t` accepts one or more literal values or file paths.
  - `--url` / `-u` accepts one or more HTTP(S) URLs or files containing URLs.
- Supplying both input modes, or neither input mode, exits with status 1.
- `--skip-defaults` / `-sk` disables the default remote Scylla and Hunter.io
  lookups. Use it for deterministic local-only searches.
- `--local-breach` / `-lb` searches clear-text breach sources.
- `--gzip` / `-gz` searches gzip-compressed breach sources.
- `--single-file` / `-sf` selects the single-file search implementation.
- `--output` / `-o` writes CSV output and `--json` / `-j` writes JSON output.
  Both may be supplied to the same invocation.
- `--gen-config` / `-g` writes `h8mail_config.ini` in the current directory,
  replacing an existing file, and exits successfully.

Searches may contact third-party services unless `--skip-defaults` is used and
no API-backed configuration is supplied. Network-backed results are inherently
dependent on those services and are not part of the deterministic output
contract.

## CSV output

CSV output has the header `Target,Type,Data`. Each two-item entry in a target's
internal result data becomes one row, in target and result order. Targets with
no matching two-item entries do not produce data rows. Fields use standard CSV
quoting and records use CRLF line endings.

The representative byte-for-byte contract is stored in
`tests/fixtures/representative-results.csv`.

## JSON output

JSON output is a top-level object with a `targets` array. Each target object has:

- `target`: the queried value;
- `pwn_num`: the target's reported breach count;
- `data`: arrays of `TYPE:value` strings grouped by source markers.

JSON is emitted as compact UTF-8 text without a trailing newline. Target and
result ordering is preserved.

The representative byte-for-byte contract is stored in
`tests/fixtures/representative-results.json`.
