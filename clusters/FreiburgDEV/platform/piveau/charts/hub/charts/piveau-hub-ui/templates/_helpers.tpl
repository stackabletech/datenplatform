{{/*
Expand the name of the chart.
*/}}
{{- define "piveau-hub-ui.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "piveau-hub-ui.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "piveau-hub-ui.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "piveau-hub-ui.labels" -}}
helm.sh/chart: {{ include "piveau-hub-ui.chart" . }}
{{ include "piveau-hub-ui.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "piveau-hub-ui.selectorLabels" -}}
app.kubernetes.io/name: {{ include "piveau-hub-ui.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "piveau-hub-ui.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "piveau-hub-ui.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create imagePullCredentials
*/}}
{{- define "imagePullCredentials" -}}
{"auths":{
{{- range $index, $val := .Values.imagePullCredentials -}}
  "{{ $val.address }}":{"username":"{{ $val.username }}","password":"{{ $val.password }}","auth":"{{ (printf "%s:%s" $val.username $val.password) | b64enc }}","email":"{{ $val.email }}"}
  {{- if (lt $index (sub (len $.Values.imagePullCredentials) 1)) -}},{{- end -}}
{{- end -}}
}}
{{- end }}

{{/*
Create imagePullSecret
*/}}
{{- define "imagePullSecret" -}}
{{ (include "imagePullCredentials" .) | b64enc }}
{{- end }}

{{/*
Create repo address
*/}}
{{- define "piveau-hub-ui.repoAddress" -}}
{{- $repoHost := default .Values.repoAddress (.Values.global).repoHost }}
{{- if and (not (hasPrefix "http://" $repoHost)) (not (hasPrefix "https://" $repoHost)) }}
{{- printf "https://%s/" $repoHost }}
{{- else }}
{{- $repoHost }}
{{- end }}
{{- end }}

{{/*
Create search address
*/}}
{{- define "piveau-hub-ui.searchAddress" -}}
{{- $searchHost := default .Values.searchAddress (.Values.global).searchHost }}
{{- if and (not (hasPrefix "http://" $searchHost)) (not (hasPrefix "https://" $searchHost)) }}
{{- printf "https://%s/" $searchHost }}
{{- else }}
{{- $searchHost }}
{{- end }}
{{- end }}
