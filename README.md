# docker-registry-cleaner


## Example usage

```yaml
version: '2.4'

services:
  registry_cleaner:
    image: junte/registry-cleaner:latest
    volumes:
    - ./rules.yml:/etc/cleaner/rules.yml
    environment:
    - REGISTRY_HOST=<host>
    - REGISTRY_USER=<username>
    - REGISTRY_PASSWORD=<password>
```

```shell script

```
