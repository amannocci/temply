# temply

Render jinja2 templates on the command line with environment variables without python runtime.

## Prerequisites
* [Python 3.6](https://docs.python.org/3/) for development.
* [Python 3.6 - Pip](https://pypi.org/project/pip/) for development.

## Features
* Render jinja2 template using command line without python environment.
* Standalone executable with jinja2 templating engine.
* Support inclusion template rendering.

## Setup
The following steps will ensure your project is cloned properly.
1. `git clone https://github.com/amannocci/temply`
2. `cd temply && ./scripts/workflow.sh setup`

## Develop
* To build `temply` in dev mode you will need to install prerequisites packages.
* Run the command below to install `temply` in dev mode into your local environment.

```bash
pip3 install --editable .
```

* You can now develop awesome `temply` features interactively by running `temply` command.

## Build
* To build you have to use the workflow script.

```bash
./scripts/workflow.sh build
```

* It will compile project code with the current environment.

## Test
* To test `temply` you have to use the workflow script.
* Tests are based on `tox`.

```bash
./scripts/workflow.sh test
```

## Release (or prepare)
* To release or prepare a release you have to use the workflow script.

```bash
./scripts/workflow.sh release
```

## How it works

* We use `PyInstaller` to create a standalone executable.
* This means you don't need python runtime to run it.
* This means also that we have a dependency with `glibc` version.
* To be compatible with a wide range of linux, we build the project using an old `glibc` version.
* If the project don't run, you will have to re-build it using your distribution.
* When the project start, it will look at the template, found the directory of the template and then configure jinja2  
the filesystem.
* It will then attempt to render the template and create a file or display on stdout.
* You can use any [jinja2](https://jinja.palletsprojects.com/en/2.11.x/templates/) syntax.

## How to render a simple configuration

* Before anything, note that you can render any file with any extension because jinja2 is based on text templating.
* Create a file where you want `/path/to/template.yml.tpl` with the following content.

```text
variable = '{{ variable }}'
another_one = '{{ another_one }}'
default_var = '{{ default_missing_var | default("default") }}'
```

* Then launch the command below to render.

```bash
variable=foo another_one=bar temply -o /path/to/template.yml /path/to/template.yml.tpl
```

* It will create a file `/path/to/template.yml` with the following content.

```yaml
variable = 'foo'
another_one = 'bar'
default_var = 'default'
```

## How to render an advanced configuration

* Create a file where you want `/path/to/template.yml.tpl` with the following content.

```text
{% include "include.yml.tpl" %}
```

* And another one at `/path/to/include.yml.tpl` with the following content.

```yaml
foobar="Hello world !"
```

* Then launch the command below to render.

```bash
temply -o /path/to/template.yml /path/to/template.yml.tpl
```

* It will create a file `/path/to/template.yml` with the following content.

```yaml
foobar="Hello world !"
```

## How to render a configuration with missing environment variables.

* Create a file where you want `/path/to/template.yml.tpl` with the following content.

```text
missing_var = '{{ missing_var }}'
```

* Then launch the command below to render.

```bash
temply --allow-missing -o /path/to/template.yml /path/to/template.yml.tpl
```

* It will create a file `/path/to/template.yml` with the following content.

```yaml
missing_var = ''
```

## How to render a configuration on stdout.

* Create a file where you want `/path/to/template.yml.tpl` with the following content.

```text
foobar="{{ foobar }}"
```

* Then launch the command below to render.

```bash
foobar='Hello world !' temply /path/to/template.yml.tpl
```

* It will output on stdout the following content.

```yaml
foobar="Hello world !"
```

## Contributing
If you find this project useful here's how you can help :

* Send a Pull Request with your awesome new features and bug fixed
* Be a part of the ommunity and help resolve [Issues](https://github.com/amannocci/temply/issues)
