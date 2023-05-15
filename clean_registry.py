import json
import logging
import os
import re
from datetime import datetime

import yaml
from dxf import DXF
from requests import HTTPError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(message)s")

registry_host = os.environ["REGISTRY_HOST"]
registry_insecure = "REGISTRY_INSECURE" in os.environ

registry_user = os.environ.get("REGISTRY_USER")
registry_password = os.environ.get("REGISTRY_PASSWORD")

rules_file = os.environ.get("RULES") or "/etc/cleaner/rules.yml"
dry_run = os.environ.get("DRY_RUN", "false") == "true"

logger.info("{0} Parameters {0}".format("*" * 5))
logger.info("host: {0}".format(registry_host))
logger.info("user: {0}".format(registry_user))
logger.info("dry run: {0}".format(dry_run))


def _auth(dxf, response):
    dxf.authenticate(registry_user, registry_password, response=response)


def _read_rules():
    with open(rules_file) as file_ptr:
        return yaml.safe_load(file_ptr)


_rules = _read_rules()


def _fetch_tags(dxf):
    fetched_aliases = {}

    try:
        for alias in dxf.list_aliases(iterate=True, batch_size=100):
            if alias == "latest":
                continue

            manifest = dxf._request("get", "manifests/" + alias).json()
            created = max(
                _parse_created(history_item) for history_item in manifest["history"]
            )

            fetched_aliases[alias] = created
    except HTTPError:
        logger.exception("Error: on load data")

    return fetched_aliases


def _parse_created(history_item):
    date_str = json.loads(history_item["v1Compatibility"])["created"]
    date_str = date_str.replace("Z", "")
    if "." in date_str:
        date_str = date_str[: date_str.index(".")]

    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")


def _clean_tags(dxf, rule, tags):
    tags = sorted(tags.items(), key=lambda alias: alias[1], reverse=True)

    for tag, created in tags[rule["retain"] :]:
        if dry_run:
            logger.info(
                '"{0}" [{1:%Y-%m-%d %H:%M:%S}] will be deleted'.format(tag, created)
            )
        else:
            try:
                dxf.del_alias(tag)
            except HTTPError as err:
                logger.warning(
                    'Error on deleting "{0}" [{1:%Y-%m-%d %H:%M:%S}]: {2}'.format(
                        tag,
                        created,
                        err,
                    )
                )
            else:
                logger.info(
                    '"{0}" [{1:%Y-%m-%d %H:%M:%S}] was deleted'.format(
                        tag,
                        created,
                    )
                )


def _clean_repository(repository):
    logger.info('{0} Processing "{1}" {0}'.format("*" * 2, repository["name"]))

    dxf = DXF(
        registry_host,
        repository["name"],
        auth=_auth if registry_user and registry_password else None,
        insecure=registry_insecure,
    )
    tags = _fetch_tags(dxf)
    tags_groups = []

    for tag_rule in repository["tags"]:
        pattern = re.compile(tag_rule["pattern"])

        matched = {}
        for tag, created in list(tags.items()):
            if pattern.match(tag):
                matched[tag] = created
                del tags[tag]

        if matched:
            tags_groups.append({"rule": tag_rule, "tags": matched})

    for tag_group in tags_groups:
        _clean_tags(dxf, tag_group["rule"], tag_group["tags"])


for repository in _rules["repositories"]:
    _clean_repository(repository)

logger.info("{0} done {0}".format("*" * 5))
