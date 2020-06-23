# docker-registry-cleaner

## Description

This tool allows cleanup target docker registry. 
You can define rules of how much tags should be retained in each tag group

## Usage

```shell script
docker run \
    -v `pwd`/rules.yml:/etc/cleaner/rules.yml \
    -e REGISTRY_HOST=<host> \
    -e REGISTRY_USER=<user> \
    -e REGISTRY_PASSWORD=<password> \
    junte/registry-cleaner:0.1.4
```

## Configuration

| Parameter        | Description       | 
| ------------- |---------------|
| REGISTRY_HOST      | docker registry address |
| REGISTRY_USER      | docker registry user    |
| REGISTRY_PASSWORD  | docker registry password |
| DRY_RUN  | dry run mode. Only show tags which will be deleted  |

## Rules definition
```yaml
repositories:
  - name: <repository path>
    tags:
      - pattern: <tag filter regex> 
        retain: <count of last tags which must be ratained>
      ...
  ...
```

### Example

This config will keep:
* keep 5 last from `rc` tags, 3 last from `dev` tags in `backend` repository. 
  Others will be deleted.
* keep 2 last in `features` path from `frontend` repository. 
  Tags from another parts will not be deleted.
* other repositories will not be processed

```yaml
repositories:
  - name: backend
    tags:
      - pattern: "rc-.*"
        retain: 5
      - pattern: "dev-.*"
        retain: 3
      - pattern: ".*"
        retain: 0
  - name: frontend
    tags:
      - pattern: "features.*"
        retain: 2
```

## Notes
* The tool only remove tags - not blobs in docker registry. 
  For full cleanup docker registry you should run:
```shell script
docker exec <registry container> bin/registry garbage-collect /etc/docker/registry/config.yml
```