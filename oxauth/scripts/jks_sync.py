import base64
import logging
import os
# import time

import consulate
from requests.exceptions import ConnectionError

GLUU_KV_HOST = os.environ.get("GLUU_KV_HOST", "localhost")
GLUU_KV_PORT = os.environ.get("GLUU_KV_PORT", 8500)

consul = consulate.Consul(host=GLUU_KV_HOST, port=GLUU_KV_PORT)

logger = logging.getLogger("jks_sync")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
fmt = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
ch.setFormatter(fmt)
logger.addHandler(ch)


def jks_created():
    b64_str = consul.kv.get("oxauth_jks_base64")
    jks = base64.b64decode(b64_str)

    with open(consul.kv.get("oxauth_openid_jks_fn"), "w") as fd:
        fd.write(jks)
        return True
    return False


def should_sync_jks():
    last_rotation = consul.kv.get("oxauth_key_rotated_at")

    # keys are not rotated yet
    if not last_rotation:
        return False

    # check modification time of local JKS
    try:
        mtime = int(os.path.getmtime(consul.kv.get("oxauth_openid_jks_fn")))
    except OSError:
        mtime = 0

    return mtime < int(last_rotation)


def sync_jks():
    if jks_created():
        logger.info("oxauth-keys.jks has been synchronized")
        return True

    # mark sync as failed
    return False


def main():
    try:
        # while True:
        logger.info("checking whether JKS should be synchronized")
        try:
            if should_sync_jks():
                sync_jks()
            else:
                logger.info("no need to sync JKS at the moment")
        except ConnectionError as exc:
            logger.warn("unable to connect to KV storage; reason={}".format(exc))

            # # sane interval
            # time.sleep(10)
    except KeyboardInterrupt:
        logger.warn("canceled by user; exiting ...")


if __name__ == "__main__":
    main()
