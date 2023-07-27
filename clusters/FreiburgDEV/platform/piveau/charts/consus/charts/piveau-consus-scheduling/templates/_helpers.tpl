{{/*
Expand the name of the chart.
*/}}
{{- define "piveau-consus-scheduling.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "piveau-consus-scheduling.fullname" -}}
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
{{- define "piveau-consus-scheduling.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "piveau-consus-scheduling.labels" -}}
helm.sh/chart: {{ include "piveau-consus-scheduling.chart" . }}
{{ include "piveau-consus-scheduling.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "piveau-consus-scheduling.selectorLabels" -}}
app.kubernetes.io/name: {{ include "piveau-consus-scheduling.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "piveau-consus-scheduling.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "piveau-consus-scheduling.fullname" .) .Values.serviceAccount.name }}
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
