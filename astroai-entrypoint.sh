#!/bin/sh
set -eu

# Railway mounts volumes after the image is built, so the mount replaces the
# image's pre-owned /data directory. Repair only that dedicated application
# mount, then permanently drop privileges before starting AstroAI.
if [ "$(id -u)" = "0" ]; then
    mkdir -p /data
    chown -R astroai:astroai /data
    exec gosu astroai "$@"
fi

exec "$@"
