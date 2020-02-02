{{ range $name, $content := . }}{{ range where $content "visibility" "public" }}
{{ $param_types := slice }}{{ range $name, $param := .defined.parameters }}{{ $param_types = $param_types | append $param.defined.type }}{{ end }}
{{ $full_url := (delimit (slice .name | append $param_types) " ") | anchorize }}

<h3 id="{{$full_url}}"><code>{{ .defined.result.type }} {{.name }} (
{{- with .defined.parameters }}{{ $n_params := len .}} {{ $id := 0 }}{{ range $name, $param := . -}}{{- $id = (add $id 1) -}}
{{ $param.defined.type }} <a href="#{{ $full_url }}-_-{{ $param.name }}">{{ $param.name }}</a>{{if lt $id $n_params}}, {{end }}
{{- end }} {{ end -}}
)</code></h3>


{{ with .defined.parameters }}
#### Parameters
{{ range $name, $param := . }}

##### {{ $name }} {#{{ $full_url }}-_-{{ $param.name }} } <!-- id="" -->
{{ $param.briefdescription | markdownify }}{{ $param.detaileddescription | markdownify }}

{{ end }}
{{ end }}

{{ with .defined.result }}{{ if .type }}
#### Result
{{ .briefdescription | markdownify }}{{ .detaileddescription | markdownify }}
{{ end }}{{ end }}

#### Description

{{ with .briefdescription }}{{ . | markdownify }}{{ end }}

{{ with .detaileddescription }}{{ . | markdownify  }}{{ end }}

{{ end }}{{ end }}
