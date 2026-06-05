FROM maven:3.9-eclipse-temurin-21
# The build phase runs --read-only with only /work (rw) and a /tmp tmpfs writable.
# Maven's local repository defaults to $HOME/.m2 (= /root/.m2): that is where `mvn
# package` downloads the build plugins (compiler, jar, surefire, resources, ...) and
# any declared dependencies on first run. Under --read-only /root is unwritable and
# the build fails. Point Maven's config dir and local repo at the writable tmpfs so
# all cache writes land in /tmp; no $HOME write is attempted.
#   MAVEN_CONFIG -> config/seed dir (stock entrypoint copies its ref content here)
#   MAVEN_ARGS   -> default CLI args applied to every `mvn` invocation:
#     -Dmaven.repo.local relocates the artifact cache to the writable tmpfs, and
#     -s pins the settings file our entrypoint generates (proxy config; see below).
ENV MAVEN_CONFIG=/tmp/.m2 \
    MAVEN_ARGS="-Dmaven.repo.local=/tmp/.m2 -s /tmp/.m2/settings.xml"
# Unlike pip/npm/cargo/go, Maven's resolver (Apache HttpClient) does NOT honor the
# HTTP(S)_PROXY env vars, nor the JVM https.proxyHost/proxyPort system properties.
# The only reliable way to route Maven Central fetches through the arena egress
# proxy is a settings.xml <proxies> block. The proxy host:port is injected per build
# (HTTPS_PROXY env, dynamic), so entrypoint.sh materializes settings.xml from that env
# at container start, then chains to the stock maven entrypoint. Maven Central's
# default host is repo.maven.apache.org (allowlisted in docker/proxy/squid.conf).
COPY entrypoint.sh /usr/local/bin/arena-entrypoint.sh
RUN chmod 0755 /usr/local/bin/arena-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/arena-entrypoint.sh"]
CMD ["mvn"]
