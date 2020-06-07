# Templaty

## Prerequisites
* [Python 3.6](https://docs.python.org/3/)

## Features
* Coming soon

## Setup
The following steps will ensure your project is cloned properly.
1. git clone https://github.com/amannocci/templaty
2. cd templaty && ./scripts/workflow.sh setup

## Build
* To build you have to use the workflow script.

```bash
./scripts/workflow.sh build
```

* It will compile project code with the current environment.

## Test
* To test `streamy` you have to use the workflow script.
* Tests are based on sbt and testcontainers capabilities.

```bash
./scripts/workflow.sh test
```

## Release (or prepare)
* To release or prepare a release you have to use the workflow script.

```bash
./scripts/workflow.sh release
```