<h1 align="center">Temply</h1>

<p align="center">
  <i>Render jinja2 templates on the command line without python runtime.</i>
</p>

<h4 align="center">
  <a href="https://github.com/techcode-io/temply/actions/workflows/ci.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/techcode-io/temply/ci.yml?branch=main&label=ci&style=flat-square" alt="continuous integration" style="height: 20px;">
  </a>
  <a href="https://github.com/techcode-io/temply/graphs/contributors">
    <img src="https://img.shields.io/github/contributors-anon/techcode-io/temply?color=yellow&style=flat-square" alt="contributors" style="height: 20px;">
  </a>
  <a href="https://opensource.org/licenses/Apache-2.0">
    <img src="https://img.shields.io/badge/apache%202.0-blue.svg?style=flat-square&label=license" alt="license" style="height: 20px;">
  </a>
  <br>
</h4>

- [Source](https://github.com/techcode-io/temply)
- [Issues](https://github.com/techcode-io/temply/issues)
- [Contact](mailto:adrien.mannocci@gmail.com)
- [Maintained by techcode.io](https://techcode.io)

## :package: Prerequisites

- [uv](https://docs.astral.sh/uv/) for build system.
- [Docker](https://docs.docker.com/) or [Podman](https://podman.io/docs) for `deb`/`rpm` packaging (Linux only).

## :sparkles: Features

- Render jinja2 template using command line without python environment.
- Standalone executable with jinja2 templating engine.
- Support inclusion template rendering, from files and stdin.
- Command line compatible with [envtpl](https://github.com/andreasjansson/envtpl).
- Load variables from environment, [envdir](#how-to-render-a-configuration-with-an-envdir),
  [dotenv](#how-to-render-a-configuration-with-a-dotenv-file) and [json](#how-to-render-a-configuration-with-a-json-file) files.
- Parse and serialize JSON and YAML values with [filters](#filters).

## :dart: Motivation

- We needed a way to generate files using data sources in a container environment.
- The solution should be standalone and delivered as a binary.

## :hammer: Workflow

### Setup

The following steps will ensure your project is cloned properly.

1. Clone repository:
   ```shell
   git clone https://github.com/techcode-io/temply
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

- It will compile project code with the current environment into `dist/temply`.
- It will also create a `dist/temply-<version>-<os>-<arch>.tar.gz` tarball.
- On Linux, `uv run poe package:deb` and `uv run poe package:rpm` build packages from `dist/temply`.

### Test

- To test `temply` you have to use the workflow.
- Tests are based on `pytest`.

```bash
uv run poe test
```

## 📖 Usage

> [!WARNING]
> By default, temply **deletes the template file** after a successful rendering.
> Use `--keep-template` to keep it.

```text
Usage: temply [OPTIONS] [INPUT_FILE]

Options:
  --allow-missing         Allow missing variables.
  --keep-template         Keep original template file (it is deleted after
                          rendering by default).
  --envdir DIRECTORY      Load environment variables from directory
  --dotenv FILE           Load environment variables from dotenv file
  --json-file FILE        Load environment variables from json file
  -o, --output-file FILE  Output file path.
  --version               Show the version and exit.
  --help                  Show this message and exit.
```

### How it works

- We use `PyInstaller` to create a standalone executable.
- This means you don't need a python runtime to run it.
- This also means it depends on the `glibc` version.
- To be compatible with a wide range of linux distributions, we build the project using an old `glibc` version.
- If the binary doesn't run, you will have to rebuild it on your distribution.
- When temply starts, it reads the template from `INPUT_FILE` (or stdin when omitted) and configures jinja2 to load
  included templates from the template directory (or the current directory for stdin).
- It then renders the template and writes the result to the output file, or to stdout.
- The output is written as is: temply doesn't add a trailing newline.
- If rendering fails (undefined variable, syntax error, invalid value), temply exits with code `1`, prints an error and
  leaves the template untouched.
- You can use any [jinja2](https://jinja.palletsprojects.com/en/3.1.x/templates/) syntax.

### Data sources

- Variables are loaded from the following sources, each one overriding the previous ones:
  1. Environment variables.
  2. `--envdir` directory.
  3. `--dotenv` file.
  4. `--json-file` file.
- This order is fixed and doesn't depend on the order of the options on the command line.

### Filters

| Filter                  | Description                                                                        |
|-------------------------|------------------------------------------------------------------------------------|
| `from_json`, `fromjson` | Parse a JSON string.                                                               |
| `to_json`, `tojson`     | Serialize a value to JSON. Replaces the jinja2 built-in `tojson` (no HTML escape). |
| `from_yaml`, `fromyaml` | Parse a YAML string.                                                               |
| `to_yaml`, `toyaml`     | Serialize a value to YAML.                                                         |

- The `environment(prefix)` function returns the `(key, value)` pairs of all variables starting with `prefix`, sorted
  by key and with the prefix removed.

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

- Templates read from stdin can include templates relative to the current directory.

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
temply --keep-template -o /path/to/template.yml /path/to/template.yml.tpl
```

- It will create a file `/path/to/template.yml` with the following content.

```yaml
foobar="Hello world !"
```

### How to render a configuration with missing environment variables

- By default, an undefined variable is an error.
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

### How to render a configuration on stdout

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

### How to render a configuration with a json environment variable

- Create a file where you want `/path/to/template.json.tpl` with the following content.

```text
first = {{ (json_var | from_json)[0] }}
all = {{ json_var | from_json | to_json }}
```

- Then launch the command below to render.

```bash
json_var='["string", 42]' temply /path/to/template.json.tpl
```

- It will output on stdout the following content.

```text
first = string
all = ["string", 42]
```

### How to render a configuration with a yaml environment variable

- Create a file where you want `/path/to/template.yaml.tpl` with the following content.

```text
foo = {{ (yaml_var | from_yaml).foo }}
{{ yaml_var | from_yaml | to_yaml }}
```

- Then launch the command below to render.

```bash
yaml_var='{foo: bar, list: [1, 2]}' temply /path/to/template.yaml.tpl
```

- It will output on stdout the following content.

```yaml
foo = bar
foo: bar
list:
- 1
- 2
```

### How to render a configuration with a wildcard environment variable

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

### How to render a configuration with an envdir

- An envdir is a directory where each file defines a variable: the file name is the key and its content the value.
- Trailing spaces, tabs and newlines are removed from the value, and `NUL` characters are replaced by newlines.
- An empty file unsets the variable, even if it's defined in the environment.
- Hidden files and subdirectories are ignored.
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
foobar="foobar"
```

### How to render a configuration with a dotenv file

- A dotenv file contains one `KEY=VALUE` per line.
- Blank lines and lines starting with `#` are ignored, and an optional `export ` prefix is allowed.
- Spaces around the key and the value are removed, as well as matching single or double quotes around the value.
- Escape sequences, variable interpolation and multiline values aren't supported.
- Create a file where you want `/path/to/template.yml.tpl` with the following content.

```text
foobar="{{ FOOBAR }}"
```

- Then create a dotenv file named `dotenv` with the following content.

```shell
# Comments are allowed
export FOOBAR="foobar"
```

- Then launch the command below to render.

```bash
temply --dotenv /path/to/dotenv /path/to/template.yml.tpl
```

- It will output on stdout the following content.

```yaml
foobar="foobar"
```

### How to render a configuration with a json file

- A json file is either an object or a list of `{"key": ..., "value": ...}` objects.
- Values keep their JSON type (string, number, list, object), and a `null` value unsets the variable.
- Create a file where you want `/path/to/template.yml.tpl` with the following content.

```text
foo="{{ FOO }}"
bar="{{ BAR }}"
```

- Then create a json file named `file.json` with the following content.

```json
{
  "FOO": "foo",
  "BAR": "bar"
}
```

- Or with the following content.

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

### How to render a configuration and keep template after rendering

- By default, temply removes the template file after rendering it.
- If you want to keep the template, use the flag `--keep-template`.
- The template is never removed when reading it from stdin or when rendering fails.

## :heart: Contributing

If you find this project useful here's how you can help, please click the :eye: **Watch** button to avoid missing
notifications about new versions, and give it a :star2: **GitHub Star**!

You can also contribute by:

- Sending a [Pull Request](https://github.com/techcode-io/temply/pulls) with your awesome new features and bug fixed.
- Be part of the community and help resolve [Issues](https://github.com/techcode-io/temply/issues).

## 🧾 License

The `temply` project is free and open-source software licensed under the Apache-2.0 license.
