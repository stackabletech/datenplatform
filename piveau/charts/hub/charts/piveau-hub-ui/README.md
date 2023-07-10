# piveau hub ui helm chart

It is important to verify the JVM heap size in javaOpts and to set the CPU/Memory resources to something suitable for your cluster.

## Install

```shell
$ helm repo add paca https://paca.fokus.fraunhofer.de/repository/helm-charts
$ helm install <release-name> paca/piveau-hub-ui
```

You can adjust your release by using the `--set parameter=value` parameter:

```shell
$ helm install --set monitoring=true <release-name> paca/piveau-hub-ui 
```

Or by passing a value file, e.g.:

```shell
$ helm install -f my-values.yaml <release-name> paca/piveau-hub-ui
```

## Upgrade

```shell
$ helm upgrade -f my-values.yaml <release-name> paca/piveau-hub-ui
```

## Configuration

| Parameter          | Description                                                                                       | Default                                                         |
|--------------------|---------------------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| `nameOverride`     | String to partially override piveau-consus-exporting-hub.fullname                                 | `""`                                                            |
| `image`            | The piveau-consus-exporting-hub Docker image                                                      | `registry.gitlab.com/piveau/consus/piveau-consus-exporting-hub` |
| `imageTag`         | The piveau-consus-exporting-hub Docker image tag                                                  | `latest`                                                        |
| `imagePullPolicy`  | The Kubernetes [imagePullPolicy][] value                                                          | `IfNotPresent`                                                  |
| `imagepullSecrets` | Configuration for [imagePullSecrets][] so that you can use a private registry for your image      | `[]`                                                            |
| `resources`        | Allows you to set the [resources][] for the deployment                                            | See [values.yaml][]                                             |
| `extraEnvs`        | Extra [environment variables][] which will be appended to the `env:` definition for the container | `[]`                                                            |
| `service.port`     | The http port that Kubernetes will use for the health checks and the service.                     | `8080`                                                          |

[environment variables]: https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/#using-environment-variables-inside-of-your-config
[imagePullPolicy]: https://kubernetes.io/docs/concepts/containers/images/#updating-images
[imagePullSecrets]: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#create-a-pod-that-uses-your-secret
[resources]: https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/
[values.yaml]: https://gitlab.com/piveau/consus/piveau-consus-exporting-hub/-/blob/master/helm/values.yaml
