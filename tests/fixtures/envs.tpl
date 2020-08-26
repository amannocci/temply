{% for key, value in environment('MY_') -%}
{{ key }} = {{ value }}
{% endfor %}