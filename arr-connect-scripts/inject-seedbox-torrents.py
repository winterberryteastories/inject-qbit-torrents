#!/usr/bin/env python3

###
### This script should be run in sonarr (Connect -> On Import Complete) & radarr (Connect -> On File Import & On File Upgrade).
### It fetches the torrent file from the seedbox qbittorrent and injects it into the local qbittorrent.
### It assumes that the files get already synced (rclone or similar) into LOCAL_QBIT_DIR.
### Then the files are already present and the local qbittorrent does not need to redownload them again.
###

import os
from pathlib import Path
import shutil
import qbittorrentapi
import requests
import logging
import time

logger = logging.getLogger('inject-seedbox-torrents')
logger.setLevel(logging.DEBUG)

LOG_FILE = os.getenv("INJECT_TORRENTS_LOG_FILE")
if LOG_FILE:
    # create file handler which logs even debug messages
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

SONARR_SOURCEPATH = 'sonarr_sourcepath'
SONARR_DOWNLOAD_ID = 'sonarr_download_id'
SONARR_DOWNLOAD_CLIENT = 'sonarr_download_client'

RADARR_MOVIEFILE_SOURCEPATH = 'radarr_moviefile_sourcepath'
RADARR_DOWNLOAD_ID = 'radarr_download_id'
RADARR_DOWNLOAD_CLIENT = 'radarr_download_client'

def main():
    LOCAL_QBIT_HOST = os.getenv("LOCAL_QBIT_HOST")
    LOCAL_QBIT_USER = os.getenv("LOCAL_QBIT_USER")
    LOCAL_QBIT_PASSWORD = os.getenv("LOCAL_QBIT_PASSWORD")

    SEEDBOX_QBIT_NAME = os.getenv("SEEDBOX_QBIT_NAME")
    SEEDBOX_QBIT_HOST = os.getenv("SEEDBOX_QBIT_HOST")
    SEEDBOX_QBIT_USER = os.getenv("SEEDBOX_QBIT_USER")
    SEEDBOX_QBIT_PASSWORD = os.getenv("SEEDBOX_QBIT_PASSWORD")

    LOCAL_QBIT_DIR = os.getenv("LOCAL_QBIT_DIR")
    if LOCAL_QBIT_DIR:
        LOCAL_QBIT_DIR = Path(LOCAL_QBIT_DIR)

    if (not LOCAL_QBIT_HOST or not LOCAL_QBIT_USER or not LOCAL_QBIT_PASSWORD or
            not SEEDBOX_QBIT_HOST or not SEEDBOX_QBIT_USER or not SEEDBOX_QBIT_PASSWORD):
        print("Missing arguments!")
        return

    CROSS_SEED_HOST = os.getenv("CROSS_SEED_HOST")
    CROSS_SEED_APIKEY = os.getenv("CROSS_SEED_APIKEY")

    # we need to connect to local and remote qbittorrent to export the torrent from the remote
    # and import it in the local one
    qb_local = qbittorrentapi.Client(host=LOCAL_QBIT_HOST,
            username=LOCAL_QBIT_USER, password=LOCAL_QBIT_PASSWORD)
    qb_seedbox = qbittorrentapi.Client(host=SEEDBOX_QBIT_HOST,
            username=SEEDBOX_QBIT_USER, password=SEEDBOX_QBIT_PASSWORD)

    qb_local.auth_log_in()
    qb_seedbox.auth_log_in()

    download_client = None
    download_id = None
    sourcepath = None

    if SONARR_DOWNLOAD_CLIENT in os.environ:
        if SONARR_SOURCEPATH not in os.environ:
            return
        if SONARR_DOWNLOAD_ID not in os.environ:
            return

        download_client = os.getenv(SONARR_DOWNLOAD_CLIENT)
        download_id = os.getenv(SONARR_DOWNLOAD_ID).lower()
        sourcepath = Path(os.getenv(SONARR_SOURCEPATH))

    elif RADARR_DOWNLOAD_CLIENT in os.environ:
        if RADARR_MOVIEFILE_SOURCEPATH not in os.environ:
            return
        if RADARR_DOWNLOAD_ID not in os.environ:
            return

        download_client = os.getenv(RADARR_DOWNLOAD_CLIENT)
        download_id = os.getenv(RADARR_DOWNLOAD_ID).lower()
        sourcepath = Path(os.getenv(RADARR_MOVIEFILE_SOURCEPATH))
    else:
        return

    # currently we want to filter and only run it for SEEDBOX_QBIT_NAME
    if download_client != SEEDBOX_QBIT_NAME:
        return

    if not sourcepath or not download_id:
        return

    logger.info(f"sourcepath: {sourcepath}")
    relative_path = sourcepath.relative_to(LOCAL_QBIT_DIR)
    save_path = LOCAL_QBIT_DIR / relative_path.parts[0]
    logger.info(f"save_path: {save_path}")

    # fetch torrent file from qbbittorrent-seedbox
    torrent_file = qb_seedbox.torrents_export(torrent_hash=download_id)

    # upload torrent file to qbittorrent-local
    qb_local.torrents_add(torrent_files=torrent_file, save_path=save_path)

    if CROSS_SEED_HOST and CROSS_SEED_APIKEY:
        # wait a bit so that the torrent was successfully added to qbittorrent-local
        time.sleep(5)

        # send it to cross-seed locally
        headers = {
            "X-Api-Key": CROSS_SEED_APIKEY,
        }
        data = {
            "infoHash": download_id,
        }
        response = requests.post(f"{CROSS_SEED_HOST}/api/webhook", headers=headers, data=data)


if __name__ == '__main__':
    main()

