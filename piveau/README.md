# piveau-hub helm chart

It is important to verify the JVM heap size in javaOpts and to set the CPU/Memory resources to something suitable for your cluster.

By default, this helm chart installs a basic piveau system, including a repository with indexing and frontend, and a consus for harvesting rdf sources. The repository and the search API are routed to the outside. Required databases are installed alongside and all necessary data is persistent.  

## Install

    helm install stackable -f values.yaml .

## Upgrade

    helm upgrade --install stackable -f values.yaml .

## Configuration

    t.b.d
        
