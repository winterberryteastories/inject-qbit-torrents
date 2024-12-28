# inject-seedbox-torrents
This allows the automatic injecting of seedbox torrents when they get imported in *arr locally.

## Prerequisites

Since I want to use [qbittorrent-api](https://pypi.org/project/qbittorrent-api/) which is python based, we first need to make sure the sonarr/radarr containers have Python available.
If you use linuxserver.io you can do the following:

Add the following line to your `volumes` in the `docker-compose.yml`:

```
- <path>/inject-seedbox-torrents/arr-custom-scripts/python.sh:/custom-cont-init.d/python.sh:ro
```

You need a setup with e.g. rclone to to sync files from your seedbox qbittorrent directory into your local qbittorrent directory (I can also include that here if there is interest).

Then in sonarr/radarr under `Settings -> Download Clients` add `Remote Path Mappings` from the seedbox qbittorrent directory to the local qbittorrent directory so sonarr/radarr can find the files.

## Step 1

Mount `arr-connect-scripts` into sonarr/radarr by adding the following line to your `volumes` in the `docker-compose.yml`:

```
- <path>/inject-seedbox-torrents/arr-connect-scripts:/arr-connect-scripts/inject-seedbox-torrents
```

## Step 2

Create a bash script in the same directory as `inject-seedbox-torrents.sh.template` (stripping the `.template`) and filling all the necessary variables.

## Step 3

Add the script `/arr-connect-scripts/inject-seedbox-torrents/inject-seedbox-torrents.sh`:

1. In Radarr under `Settings -> Connect` as `Custom Script` with `On File Import` & `On File Upgrade` as trigger.
2. In Sonarr under `Settings -> Connect` as `Custom Script` with `On Import Complete` as trigger.
