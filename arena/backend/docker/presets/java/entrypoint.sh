#!/bin/sh -eu
# Generate Maven's proxy + local-repo settings from the runtime environment, then
# hand off to the stock maven entrypoint (which seeds MAVEN_CONFIG and exec's "$@").
#
# WHY THIS EXISTS: unlike pip / npm / cargo / go, Maven's resolver (Apache HttpClient)
# does NOT honor the HTTP(S)_PROXY environment variables, and it does NOT honor the
# JVM https.proxyHost/proxyPort system properties either. The only reliable way to
# route Maven Central fetches through the arena egress-allowlist proxy is a settings.xml
# <proxies> block. The proxy host:port is injected per build (HTTPS_PROXY env, dynamic),
# so we materialize settings.xml at container start from that env. MAVEN_ARGS pins the
# settings path with `-s`, so the default `mvn -q package` build command needs no change.
#
# The build phase (networked) sets HTTPS_PROXY -> we emit a <proxy>; the run phase uses
# `java -jar` (not mvn) and has no HTTPS_PROXY, but we still emit a valid (proxy-less)
# settings.xml so the pinned `-s` path always resolves.

SETTINGS_DIR="${MAVEN_CONFIG:-/tmp/.m2}"
SETTINGS_FILE="${SETTINGS_DIR}/settings.xml"
mkdir -p "${SETTINGS_DIR}"

# Prefer HTTPS_PROXY, fall back to lowercase / HTTP_PROXY (squid handles both schemes).
proxy_url="${HTTPS_PROXY:-${https_proxy:-${HTTP_PROXY:-${http_proxy:-}}}}"

if [ -n "${proxy_url}" ]; then
  # Parse http://host:port -> host, port (strip scheme, optional trailing slash).
  stripped="${proxy_url#*://}"
  stripped="${stripped%/}"
  proxy_host="${stripped%%:*}"
  proxy_port="${stripped##*:}"
  [ "${proxy_port}" = "${stripped}" ] && proxy_port=3128   # no :port in URL -> default
  # Both http and https artifact protocols route through the same CONNECT proxy.
  cat > "${SETTINGS_FILE}" <<EOF
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0">
  <proxies>
    <proxy>
      <id>arena-egress-http</id>
      <active>true</active>
      <protocol>http</protocol>
      <host>${proxy_host}</host>
      <port>${proxy_port}</port>
    </proxy>
    <proxy>
      <id>arena-egress-https</id>
      <active>true</active>
      <protocol>https</protocol>
      <host>${proxy_host}</host>
      <port>${proxy_port}</port>
    </proxy>
  </proxies>
</settings>
EOF
else
  cat > "${SETTINGS_FILE}" <<EOF
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"/>
EOF
fi

exec /usr/local/bin/mvn-entrypoint.sh "$@"
