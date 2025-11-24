<h1 style="margin-left: auto; margin-right: auto;">Temply</h1>

<p style="margin-left: auto; margin-right: auto;">
  <i>Render jinja2 templates on the command line without python runtime.</i>
</p>

<h4 style="margin-left: auto; margin-right: auto;">
  <a href="[https://github.com/amannocci/temply/actions/workflows/ci.yml](https://github.com/amannocci/temply/actions/workflows/ci.yml)">
    <img src="https://img.shields.io/github/actions/workflow/status/amannocci/temply/ci.yml?branch=main&label=ci&style=flat-square" alt="continuous integration" style="height: 20px;">
  </a>
  <a href="https://github.com/amannocci/temply/graphs/contributors">
    <img src="https://img.shields.io/github/contributors-anon/amannocci/temply?color=yellow&style=flat-square" alt="contributors" style="height: 20px;">
  </a>
  <a href="https://opensource.org/licenses/Apache-2.0">
    <img src="https://img.shields.io/badge/apache%202.0-blue.svg?style=flat-square&label=license" alt="license" style="height: 20px;">
  </a>
  <br>
</h4>

- [Source](https://github.com/amannocci/temply)
- [Issues](https://github.com/amannocci/temply/issues)
- [Contact](mailto:adrien.mannocci@gmail.com)

## :package: Prerequisites

- [Python 3.12+](https://docs.python.org/3/) for development.
- [uv](https://docs.astral.sh/uv/) for build system.
- [Poe](https://poethepoet.natn.io/installation.html) for task runner.
- [Podman](https://podman.io/docs) for container packaging.
- [pre-commit](https://pre-commit.com/) for git management.

## :sparkles: Features

- Render jinja2 template using command line without python environment.
- Standalone executable with jinja2 templating engine.
- Support inclusion template rendering.
- Command line fully compatible with [envtpl](https://github.com/andreasjansson/envtpl).
- Support loading from environment variables.

## :dart: Motivation

- We needed a way to generate files using data sources in a container environment.
- The solution should be standalone and delivered as a binary.

## :hammer: Workflow

### Setup

The following steps will ensure your project is cloned properly.

1. Clone repository:
   ```shell
   git clone https://github.com/amannocci/temply
   cd temply
   ```
2. Install dependencies and setup environment:
   ```shell
   uv sync
   uv run poe env:configure
   ```

### Lint

- To lint you have to use the workflow.

```bash
uv run poe lint
```

### Format

- To format you have to use the workflow.

```bash
uv run poe fmt
```

- It will format the project code using `ruff`.

### Build

- To build you have to use the workflow.

```bash
uv run poe build
```

- It will compile project code with the current environment.

### Test

- To test `temply` you have to use the workflow.
- Tests are based on `pytest`.

```bash
uv run poe test
```

## 📖 Usage

### How it works

- We use `PyInstaller` to create a standalone executable.
- This means you don't need python runtime to run it.
- This means also that we have a dependency with `glibc` version.
- To be compatible with a wide range of linux, we build the project using an old `glibc` version.
- If the project don't run, you will have to re-build it using your distribution.
- When the project start, it will look at the template, found the directory of the template and then configure jinja2
  the filesystem.
- It will then attempt to render the template and create a file or display on stdout.
- You can use any [jinja2](https://jinja.palletsprojects.com/en/3.1.x/templates/) syntax.

### How to render a simple configuration

- Before anything, note that you can render any file with any extension because jinja2 is based on text templating.
- Create a file where you want `/path/to/template.yml.tpl` with the following content.

```text
variable = '{{ variable }}'
another_one = '{{ another_one }}'
default_var = '{{ default_missing_var | default("default") }}'
```

- Then launch the command below to render.

```bash
variable=foo another_one=bar temply -o /path/to/template.yml /path/to/template.yml.tpl
```

- It will create a file `/path/to/template.yml` with the following content.

```yaml
variable = 'foo'
another_one = 'bar'
default_var = 'default'
```

### How to render a configuration from stdin

- Launch the command below to render.

```bash
echo 'Hello {{ name }} !' | name=world temply -o /path/to/template.txt
```

- It will create a file `/path/to/template.txt` with the following content.

```text
Hello world !

```

### How to render an advanced configuration

- Create a file where you want `/path/to/template.yml.tpl` with the following content.

```text
{% include "include.yml.tpl" %}
```

- And another one at `/path/to/include.yml.tpl` with the following content.

```yaml
foobar="Hello world !"
```

- Then launch the command below to render.

```bash
temply -o /path/to/template.yml /path/to/template.yml.tpl
```

- It will create a file `/path/to/template.yml` with the following content.

```yaml
foobar="Hello world !"
```

### How to render a configuration with missing environment variables.

- Create a file where you want `/path/to/template.yml.tpl` with the following content.

```text
missing_var = '{{ missing_var }}'
```

- Then launch the command below to render.

```bash
temply --allow-missing -o /path/to/template.yml /path/to/template.yml.tpl
```

- It will create a file `/path/to/template.yml` with the following content.

```yaml
missing_var = ''
```

### How to render a configuration on stdout.

- Create a file where you want `/path/to/template.yml.tpl` with the following content.

```text
foobar="{{ foobar }}"
```

- Then launch the command below to render.

```bash
foobar='Hello world !' temply /path/to/template.yml.tpl
```

- It will output on stdout the following content.

```yaml
foobar="Hello world !"
```

### How to render a configuration with a json environment variable.

- Create a file where you want `/path/to/template.json.tpl` with the following content.

```text
{{ json_var | fromjson }}
# Or {{ json_var | from_json }}
```

- Then launch the command below to render.

```bash
json_var='["string"]' temply /path/to/template.json.tpl
```

- It will output on stdout the following content.

```json
["string"]
```

### How to render a configuration with a yaml environment variable.

- Create a file where you want `/path/to/template.yaml.tpl` with the following content.

```text
{{ (yaml_var | fromyaml).foo }}
# Or {{ (yaml_var | from_yaml).foo }}
```

- Then launch the command below to render.

```bash
yaml_var='foo: bar' temply /path/to/template.yaml.tpl
```

- It will output on stdout the following content.

```text
bar
```

### How to render a configuration with a wildcard environment variable.

- Create a file where you want `/path/to/template.yml.tpl` with the following content.

```text
{% for key, value in environment('MY_') -%}
{{ key }} = {{ value }}
{% endfor %}
```

- Then launch the command below to render.

```bash
MY_FOO=foo MY_BAR=bar temply /path/to/template.yml.tpl
```

- It will output on stdout the following content.

```yaml
BAR = bar
FOO = foo
```

### How to render a configuration with an envdir.

- Create a file where you want `/path/to/template.yml.tpl` with the following content.

```text
foobar="{{ FOOBAR }}"
```

- Then create an envdir with a file named `FOOBAR` with `foobar` as content.
- Then launch the command below to render.

```bash
temply --envdir /path/to/envdir /path/to/template.yml.tpl
```

- It will output on stdout the following content.

```yaml
foobar = foobar
```

### How to render a configuration with a dotenv file.

- Create a file where you want `/path/to/template.yml.tpl` with the following content.

```text
foobar="{{ FOOBAR }}"
```

- Then create a dotenv file named `dotenv` with `FOOBAR=foobar` as content.
- Then launch the command below to render.

```bash
temply --dotenv /path/to/dotenv /path/to/template.yml.tpl
```

- It will output on stdout the following content.

```yaml
foobar = foobar
```

### How to render a configuration with a json file.

- Create a file where you want `/path/to/template.yml.tpl` with the following content.

```text
foo="{{ FOO }}"
bar="{{ BAR }}"
```

- Then create a json file named `file.json` with the following content.

```json
[
  {
    "key": "FOO",
    "value": "foo"
  },
  {
    "key": "BAR",
    "value": "bar"
  }
]
```

- Then launch the command below to render.

```bash
temply --json-file /path/to/file.json /path/to/template.yml.tpl
```

- It will output on stdout the following content.

```yaml
foo="foo"
bar="bar"
```

### How to render a configuration and keep template after rendering.

- By default, temply will remove template file.
- If you want to keep template you will have to use the flag `--keep-template`.

## :heart: Contributing

If you find this project useful here's how you can help, please click the :eye: **Watch** button to avoid missing
notifications about new versions, and give it a :star2: **GitHub Star**!

You can also contribute by:

- Sending a [Pull Request](https://github.com/amannocci/temply/pulls) with your awesome new features and bug fixed.
- Be part of the community and help resolve [Issues](https://github.com/amannocci/temply/issues).

## 🧾 License

The `temply` project is free and open-source software licensed under the Apache-2.0 license.
