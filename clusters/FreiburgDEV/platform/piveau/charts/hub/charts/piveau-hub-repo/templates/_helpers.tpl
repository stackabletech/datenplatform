{{/*
Expand the name of the chart.
*/}}
{{- define "piveau-hub-repo.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "piveau-hub-repo.fullname" -}}
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
{{- define "piveau-hub-repo.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "piveau-hub-repo.labels" -}}
helm.sh/chart: {{ include "piveau-hub-repo.chart" . }}
{{ include "piveau-hub-repo.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "piveau-hub-repo.selectorLabels" -}}
app.kubernetes.io/name: {{ include "piveau-hub-repo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "piveau-hub-repo.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "piveau-hub-repo.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create a name for the virtuoso triple store
*/}}
{{- define "piveau-hub-repo.virtuosoName" -}}
{{- $name := "virtuoso" }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}


{{/*
Virtuoso common labels
*/}}
{{- define "piveau-hub-repo.virtuosoLabels" -}}
helm.sh/chart: {{ include "piveau-hub-repo.chart" . }}
{{ include "piveau-hub-repo.virtuosoSelectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Virtuoso selector labels
*/}}
{{- define "piveau-hub-repo.virtuosoSelectorLabels" -}}
app.kubernetes.io/name: "virtuoso"
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
