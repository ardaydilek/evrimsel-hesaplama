FROM node:20
# The build phase runs --read-only with only /work (rw) and a /tmp tmpfs writable.
# npm's default cache is $HOME/.npm (= /root/.npm), which is unwritable under
# --read-only and makes `npm ci`/`npm install` fail with ENOENT mkdir /root/.npm.
# Point the cache at the writable tmpfs; npm nests its logs (_logs) and
# update-notifier state under the cache dir, so no $HOME write is ever attempted.
ENV npm_config_cache=/tmp/.npm
# No update-notifier network/file side-effects during locked-down builds.
ENV npm_config_update_notifier=false
