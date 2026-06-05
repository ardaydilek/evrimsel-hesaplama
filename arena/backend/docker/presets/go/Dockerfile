FROM golang:1.22
# The build phase runs --read-only with only /work (rw) and a /tmp tmpfs writable.
# go's default caches live under $HOME (= /root): the build cache GOCACHE
# (/root/.cache/go-build) and the module cache under GOPATH (/root/go/pkg/mod).
# Both are unwritable under --read-only and make `go build` fail with permission
# errors. Point GOPATH and GOCACHE at the writable tmpfs so all cache writes land
# in /tmp; no $HOME write is ever attempted.
ENV GOPATH=/tmp/go \
    GOCACHE=/tmp/.gocache \
    GOFLAGS=-mod=mod
# -mod=mod lets `go build` add missing go.sum entries for modules fetched at build
# time. GOPROXY defaults to https://proxy.golang.org and go honors HTTPS_PROXY, so
# module fetches route through the squid egress-allowlist proxy. Module checksums
# are still verified against GOSUMDB (sum.golang.org, also allowlisted).
