FROM rust:1.78
# The build phase runs --read-only with only /work (rw) and a /tmp tmpfs writable.
# The official rust image sets CARGO_HOME=/usr/local/cargo; that is where `cargo
# build` writes the registry index and the downloaded/extracted crate sources.
# Under --read-only that path is unwritable and the build fails with permission
# errors. Point CARGO_HOME at the writable tmpfs so all cache writes land in /tmp.
# (Compiled output goes to ./target in /work, which is rw in the build phase.
# RUSTUP_HOME is only used for toolchain management, never written by `cargo build`,
# so it is left at its image default.)
ENV CARGO_HOME=/tmp/.cargo
# cargo's default sparse protocol fetches the index from index.crates.io and crates
# from static.crates.io over HTTPS, and cargo honors HTTPS_PROXY, so dependency
# fetches route through the squid egress-allowlist proxy in the networked build phase.
