# piveau scheduling
Microservice for scheduling pipes.

## Table of Contents
1. [Build](#build)
1. [Run](#run)
1. [Interface](#interface)
1. [Docker](#docker)
1. [Configuration](#configuration)
    1. [Environment](#environment)
    1. [Logging](#logging)
1. [License](#license)

## Build
Requirements:
 * Git
 * Maven 3
 * Java 11

```bash
$ git clone <gitrepouri>
$ cd piveau-consus-scheduling
$ mvn package
```

## Run

```bash
$ java -jar target/scheduling.jar
```

## Interface

The documentation of the REST service can be found when the root context is opened in a browser. It is based on the OpenAPI specification stored at `src/main/resources/webroot/openapi.yaml`.

```
http://localhost:8080/
```

## Shell

The Shell can be found under the configured port, for example:

```
http://localhost:8085/shell.html
```

### Available commands

| Command | Description | 
| :--- | :--- | 
| `pipes` | List available pipes. | 
| `show <pipe-id>` | Show specific pipe. | 
| `trigger <pipe-id>` | Show triggers of specific pipe. | 
| `launch <pipe-id>` | Start specific pipe immediately. | 

To create/update/delete triggers use the provided REST API.


## Docker

Build docker image:
```bash
$ docker build -t piveau/piveau-consus-scheduling .
```

Run docker image:
```bash
$ docker run -it -p 8080:8080 piveau/piveau-consus-scheduling
```

## Configuration

### Environment
| Variable| Description | Default Value |
| :--- | :--- | :--- |
| `PORT` | Port this service will run on. | `8080` |
| `PIVEAU_CLUSTER_CONFIG` | Json object describing the mapping between service name and endpoint. | _No default value_ |
| `PIVEAU_SHELL_CONFIG` | Json object describing shell endpoints. | _No default value_ |
| `PIVEAU_FAVICON_PATH` | Path to favicon, used in OpenAPI rendering. | `webroot/images/favicon.png` |
| `PIVEAU_LOGO_PATH` | Path to logo, used in OpenAPI rendering. | `webroot/images/logo.png` |

### Logging
See [logback](https://logback.qos.ch/documentation.html) documentation for more details

| Variable| Description | Default Value |
| :--- | :--- | :--- |
| `PIVEAU_PIPE_LOG_APPENDER` | Configures the log appender for the pipe context | `STDOUT` |
| `LOGSTASH_HOST`            | The host of the logstash service | `logstash` |
| `LOGSTASH_PORT`            | The port the logstash service is running | `5044` |
| `PIVEAU_PIPE_LOG_PATH`     | Path to the file for the file appender | `logs/piveau-pipe.%d{yyyy-MM-dd}.log` |
| `PIVEAU_PIPE_LOG_LEVEL`    | The log level for the pipe context | `INFO` |

## License

[Apache License, Version 2.0](LICENSE.md)
