{{ $ns_def := dict }}
{{ $ns_data := $.Site.Data.docs.doxdata }}
{{ with .Get 0 }}
{{   range ($ns := (split . ".")) }}
{{     if and (isset $ns_data "namespaces") (isset (index $ns_data "namespaces") .) }}
{{       $ns_def = (index $ns_data "namespaces" .) }}
{{       $ns_data = (index $ns_def "defined") }}
{{     else if and (isset $ns_data "types") (isset (index $ns_data "types") .) }}
{{       $ns_def = (index $ns_data "types" .) }}
{{       $ns_data = (index $ns_def "defined") }}
{{     end }}
{{   end }}
{{ end }}

{{ with $ns_def.briefdescription }}{{ . | markdownify }}{{ end }}

{{ with $ns_def.detaileddescription }}{{ . | markdownify  }}{{ end }}

{{ with $ns_data }}

{{ with .types }}
## Member types
{{ range $name, $content := . }}
[`{{ $content.defined.kind }} {{ $name }}`]( {{ $name | lower | replaceRE "[^a-z0-9]" "_" }} )
:    {{ with $content.briefdescription }}{{ . }}{{ end }}
{{- end }}{{ end }}

{{ with .functions }}
## Member Functions
{{ partial "function_list.html" . }}
{{ end }}

{{ with .variables }}{{ with where . "visibility" "public" }}
## Member Variables
{{ partial "variable_list.html" . }}
{{ end }}{{ end }}

{{ with .functions }}
## Member Function Documentation
{{ partial "function_detailed_list.md" . }}
{{ end }}

{{ end }}
