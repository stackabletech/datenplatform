# piveau hub search helm chart

It is important to verify the JVM heap size in javaOpts and to set the CPU/Memory resources to something suitable for your cluster.

## Install

```shell
$ helm repo add paca https://paca.fokus.fraunhofer.de/repository/helm-charts
$ helm install <release-name> paca/piveau-hub-search
```

You can adjust your release by using the `--set parameter=value` parameter:

```shell
$ helm install --set monitoring=true <release-name> paca/piveau-hub-search 
```

Or by passing a value file, e.g.:

```shell
$ helm install -f my-values.yaml <release-name> paca/piveau-hub-search
```

## Upgrade

```shell
$ helm upgrade -f my-values.yaml <release-name> paca/piveau-hub-search
```

## Configuration

| Parameter             | Description                                                                                       | Default                                                        |
|-----------------------|---------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| `nameOverride`        | String to partially override piveau-hub-search.fullname                                           | `""`                                                           |
| `image`               | The piveau-hub-search Docker image                                                                | `registry.gitlab.com/piveau/hub/piveau-hub-search`             |
| `imageTag`            | The piveau-hub-search Docker image tag                                                            | `4.0.9`                                                        |
| `imagePullPolicy`     | The Kubernetes [imagePullPolicy][] value                                                          | `IfNotPresent`                                                 |
| `imagepullSecrets`    | Configuration for [imagePullSecrets][] so that you can use a private registry for your image      | `[]`                                                           |
| `resources`           | Allows you to set the [resources][] for the deployment                                            | See [values.yaml][]                                            |
| `extraEnvs`           | Extra [environment variables][] which will be appended to the `env:` definition for the container | `[]`                                                           |
| `javaOpts`            | Java options for piveau-hub-search. This is where you could configure the jvm heap size           | `-XX:MaxRAMPercentage=75.0`                                    |
| `service.port`        | The http port that Kubernetes will use for the health checks and the service.                     | `8080`                                                         |
| `apiKey`              | The api key to use                                                                                | `apiKey`                                                       |
| `ingress.enabled`     | Enables ingress route for external service access                                                 | `false`                                                        |
| `ingress.annotations` | Additional ingress annotations                                                                    | `{}`                                                           |
| `ingress.host`        | Host for the ingress route                                                                        | `search.example.local`                                         |
| `ingress.path`        | Path for the ingress route                                                                        | `/`                                                            |
| `ingress.pathType`    | Path type for the ingress route                                                                   | `ImplementationSpecific`                                       |
| `ingress.extraHosts`  | Array f extra host for ingress routes                                                             | See [values.yaml][]                                            |
| `cli.enabled`         | Enables command line interface                                                                    | `false`                                                        |
| `cli.http`            | Configure http command line interface                                                             | `{}`                                                           |
| `cli.telnet`          | Configure telnet command line interface                                                           | `{}`                                                           |
| `elasticsearch`       | Configure the underlying elasticsearch deployment                                                 | See [values][values elasticsearch] of elasticsearch helm chart |

[environment variables]: https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/#using-environment-variables-inside-of-your-config
[imagePullPolicy]: https://kubernetes.io/docs/concepts/containers/images/#updating-images
[imagePullSecrets]: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#create-a-pod-that-uses-your-secret
[resources]: https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/
[values.yaml]: https://gitlab.com/piveau/hub/piveau-hub-search/-/blob/master/helm/values.yaml
[values elasticsearch]: https://github.com/elastic/helm-charts/tree/7.17/elasticsearch/values.yaml
