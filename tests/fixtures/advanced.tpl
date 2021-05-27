{{ simple }}
{{ foobar | default('foobar') }}
{% if foo is defined %}
defined
{% else %}
undefined
{% endif %}