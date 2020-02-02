{{ $ns_def := dict }}
{{ $ns_data := $.Site.Data.docs.doxdata }}
{{ with .Get 0 }}
{{   range (split . ".") }}
{{     $ns_def = (index $ns_data "namespaces" .) }}
{{     $ns_data = (index $ns_def "defined") }}
{{   end }}
{{ end }}

{{ with $ns_def.briefdescription }}{{ . }}{{ end }}

{{ with $ns_def.detaileddescription }}{{ . }}{{ end }}

{{ with $ns_data }}

{{ with .namespaces }}
## Namespaces:
{{ range $name, $content := . }}
[`{{ $name }}`]({{ $name | lower | replaceRE "[^a-z0-9]" "_" }})
:    {{ with $content.briefdescription }}{{ . }}{{ end }}
{{- end }}{{ end }}

{{ with .types }}
## Types:
{{ range $name, $content := . }}
[`{{ $content.defined.kind }} {{ $name }}`]( {{ $name | lower | replaceRE "[^a-z0-9]" "_" }} )
:    {{ with $content.briefdescription }}{{ . }}{{ end }}
{{- end }}{{ end }}

{{ with .functions }}
## Functions:
{{ range $name, $content := . }}{{ range $content }}
[`{{ $name }}`]( #{{ $name | lower | replaceRE "[^a-z0-9]" "_" }} )
:    {{ with .briefdescription }}{{ . }}{{ end }}
{{- end }}{{ end }}{{ end }}

{{ with .variables }}
## Global variables:
{{ range $name, $content := . }}
[`{{ $name }}`]( #{{ $name | lower | replaceRE "[^a-z0-9]" "_" }} )
:    {{ with $content.briefdescription }}{{ . }}{{ end }}
{{- end }}{{ end }}

{{ end }}
