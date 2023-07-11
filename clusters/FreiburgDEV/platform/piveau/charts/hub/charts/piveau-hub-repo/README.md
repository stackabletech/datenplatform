# piveau hub repo helm chart

It is important to verify the JVM heap size in javaOpts and to set the CPU/Memory resources to something suitable for your cluster.

## Install

```shell
$ helm repo add paca https://paca.fokus.fraunhofer.de/repository/helm-charts
$ helm install <release-name> paca/piveau-hub-repo
```

You can adjust your release by using the `--set parameter=value` parameter:

```shell
$ helm install --set monitoring=true <release-name> paca/piveau-hub-repo 
```

Or by passing a value file, e.g.:

```shell
$ helm install -f my-values.yaml <release-name> paca/piveau-hub-repo
```

## Upgrade

```shell
$ helm upgrade -f my-values.yaml <release-name> paca/piveau-hub-repo
```

## Configuration

| Parameter                      | Description                                                                                                         | Default                                          |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|
| `nameOverride`                 | String to partially override piveau-hub-repo.fullname                                                               | `""`                                             |
| `image`                        | The piveau-hub-repo Docker image                                                                                    | `registry.gitlab.com/piveau/hub/piveau-hub-repo` |
| `imageTag`                     | The piveau-hub-repo Docker image tag                                                                                | `2.1.1`                                          |
| `imagePullPolicy`              | The Kubernetes [imagePullPolicy][] value                                                                            | `IfNotPresent`                                   |
| `imagepullSecrets`             | Configuration for [imagePullSecrets][] so that you can use a private registry for your image                        | `[]`                                             |
| `resources`                    | Allows you to set the [resources][] for the deployment                                                              | See [values.yaml][]                              |
| `extraEnvs`                    | Extra [environment variables][] which will be appended to the `env:` definition for the container                   | `[]`                                             |
| `javaOpts`                     | Java options for piveau-hub-repo. This is where you could configure the jvm heap size                               | `-XX:MaxRAMPercentage=75.0`                      |
| `service.port`                 | The http port that Kubernetes will use for the health checks and the service.                                       | `8080`                                           |
| `ingress.enabled`              | Enables ingress route for external service access                                                                   | `false`                                          |
| `ingress.annotations`          | Additional ingress annotations                                                                                      | `{}`                                             |
| `ingress.hosts`                | Array of hosts for the ingress route                                                                                | See [values.yaml][]                              |
| `cli.enabled`                  | Enables command line interface                                                                                      | `false`                                          |
| `cli.http`                     | Configure http command line interface                                                                               | `{}`                                             |
| `cli.telnet`                   | Configure telnet command line interface                                                                             | `{}`                                             |
| `virtuoso.image`               | The OpenLink Virtuoso Docker image                                                                                  | `openlink/virtuoso-opensource-7`                 |
| `virtuoso.imageTag`            | The OpenLink Virtuoso Docker image tag                                                                              | `7.2.8`                                          |
| `virtuoso.imagePullPolicy`     | The Kubernetes [imagePullPolicy][] value for the OpenLink Virtuoso                                                  | `IfNotPresent`                                   |
| `virtuoso.password`            | Set the initial password for the OpenLink Virtuoso                                                                  | `dba`                                            |
| `virtuoso.resources`           | Allows you to set the [resources][] for the OpenLink Virtuoso deployment                                            | See [values.yaml][]                              |
| `virtuoso.extraEnvs`           | Extra [environment variables][] which will be appended to the `env:` definition for the OpenLink Virtuoso container | `[]`                                             |
| `virtuoso.service.port`        | The http port that Kubernetes will use for the health checks and the service of the OpenLink Virtuoso.              | `8890`                                           |
| `virtuoso.persistence.enabled` | Enables persistence for the OpenLink Virtuoso                                                                       | `true`                                           |
| `virtuoso.persistence.size`    | Persistence storage size                                                                                            | `100Gi`                                          |
| `virtuoso.ingress.enabled`     | Enables ingress route for external OpenLink Virtuoso service access                                                 | `false`                                          |
| `virtuoso.ingress.annotations` | Additional ingress annotations for OpenLink Virtuoso                                                                | `{}`                                             |
| `virtuoso.ingress.hosts`       | Array of hosts for the OpenLink Virtuoso ingress route                                                              | See [values.yaml][]                              |

[environment variables]: https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/#using-environment-variables-inside-of-your-config
[imagePullPolicy]: https://kubernetes.io/docs/concepts/containers/images/#updating-images
[imagePullSecrets]: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#create-a-pod-that-uses-your-secret
[resources]: https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/
[values.yaml]: https://gitlab.com/piveau/hub/piveau-hub-repo/-/blob/master/helm/values.yaml
