# tests/integration/test_container_integration.py
import pytest

from arena_core import problem
from arena_core.container_runner import ContainerRunner
from arena_core.run_spec import RunSpec, ResourceLimits
from arena_core.scorer import score_stdout

pytestmark = pytest.mark.docker

IDENTITY = "print('TOUR ' + ' '.join(str(c) for c in range(1, 43)))"
MATRIX = problem.load_distance_matrix()


def test_python_identity_scores_699():
    r = ContainerRunner().run(RunSpec(preset="python", files={"main.py": IDENTITY}))
    assert r.status == "ok", r.stderr
    assert score_stdout(r.stdout, MATRIX).length == 699


def test_cpp_builds_and_scores_699():
    # Prints the identity tour (1..42); its closed-tour length is the optimum, 699.
    # Proves the compile (make) -> run (./solver) -> score path. The Makefile recipe
    # line MUST be tab-indented (make requires a leading TAB, not spaces).
    cpp = ('#include <cstdio>\n'
           'int main(){ printf("TOUR"); for(int i=1;i<=42;i++) printf(" %d", i);'
           ' printf("\\n"); return 0; }\n')
    files = {"main.cpp": cpp, "Makefile": "all:\n\tg++ -O2 main.cpp -o solver\n"}
    r = ContainerRunner().run(RunSpec(preset="cpp", files=files))
    assert r.status == "ok", r.stderr
    assert score_stdout(r.stdout, MATRIX).length == 699


def test_run_phase_has_no_network():
    src = ("import socket\n"
           "try:\n"
           "    socket.create_connection(('1.1.1.1', 53), timeout=3)\n"
           "    print('NET_OK')\n"
           "except OSError:\n"
           "    print('NET_BLOCKED')\n")
    r = ContainerRunner().run(RunSpec(preset="python", files={"main.py": src}))
    assert r.status == "ok", r.stderr
    assert "NET_BLOCKED" in r.stdout            # --network none in the run phase


def test_infinite_loop_times_out():
    r = ContainerRunner(run_limits=ResourceLimits(256, 1.0, 3, 128, 100_000)).run(
        RunSpec(preset="python", files={"main.py": "while True:\n    pass\n"}))
    assert r.status == "timeout"


def test_build_failure_reports_error():
    files = {"main.cpp": "int main(){ this is not valid c++ }\n",
             "Makefile": "all:\n\tg++ -O2 main.cpp -o solver\n"}
    r = ContainerRunner().run(RunSpec(preset="cpp", files=files))
    assert r.status == "error"
    assert r.stderr                             # compiler diagnostics surfaced


def test_node_fetches_dependency_through_proxy_then_runs_offline():
    # `npm install` fetches is-number from registry.npmjs.org through the allowlist proxy
    # (build phase, networked); then `node main.js` runs with --network none and prints a tour.
    files = {
        "package.json": '{"name":"s","version":"1.0.0","dependencies":{"is-number":"^7.0.0"}}',
        "main.js": ("const isNumber = require('is-number');\n"
                    "if (!isNumber(42)) { process.exit(1); }\n"
                    "const t = []; for (let i = 1; i <= 42; i++) t.push(i);\n"
                    "console.log('TOUR ' + t.join(' '));\n"),
    }
    # node default build is `npm ci` (needs a lockfile); override to `npm install` here.
    r = ContainerRunner().run(RunSpec(preset="node", files=files, build_cmd="npm install"))
    assert r.status == "ok", r.stderr
    assert score_stdout(r.stdout, MATRIX).length == 699


def test_go_fetches_dependency_through_proxy_then_runs_offline():
    # `go build` fetches rsc.io/quote (+ its transitive deps) from proxy.golang.org
    # through the egress-allowlist proxy (build phase, networked), verifying checksums
    # against sum.golang.org (also allowlisted) and writing caches to the /tmp tmpfs
    # (GOPATH/GOCACHE redirected in the image since $HOME is read-only). Then ./solver
    # runs with --network none and prints the identity tour (1..42), length 699.
    # quote.Hello() forces the dependency to actually be fetched and linked.
    files = {
        "go.mod": "module solver\n\ngo 1.21\n\nrequire rsc.io/quote v1.5.2\n",
        "main.go": (
            "package main\n\n"
            "import (\n"
            "\t\"fmt\"\n"
            "\t\"rsc.io/quote\"\n"
            ")\n\n"
            "func main() {\n"
            "\t_ = quote.Hello()\n"
            "\tfmt.Print(\"TOUR\")\n"
            "\tfor i := 1; i <= 42; i++ {\n"
            "\t\tfmt.Printf(\" %d\", i)\n"
            "\t}\n"
            "\tfmt.Println()\n"
            "}\n"
        ),
    }
    r = ContainerRunner().run(RunSpec(preset="go", files=files))
    assert r.status == "ok", r.stderr
    assert score_stdout(r.stdout, MATRIX).length == 699


def test_rust_fetches_dependency_through_proxy_then_runs_offline():
    # `cargo build --release` fetches the itoa crate (tiny, zero-dependency) through
    # the egress-allowlist proxy (build phase, networked): cargo's default sparse
    # protocol pulls the index from index.crates.io and the crate from
    # static.crates.io (both allowlisted), honoring HTTPS_PROXY. CARGO_HOME is
    # redirected to the /tmp tmpfs in the image since /usr/local/cargo is unwritable
    # under --read-only. Then ./target/release/solver runs with --network none and
    # prints the identity tour (1..42), length 699. Using itoa::Buffer forces the
    # dependency to actually be fetched and linked (proving the proxied build). The
    # package name MUST be `solver` so the default run_cmd ./target/release/solver
    # matches the produced binary.
    cargo_toml = (
        "[package]\n"
        'name = "solver"\n'
        'version = "0.1.0"\n'
        'edition = "2021"\n\n'
        "[dependencies]\n"
        'itoa = "1"\n'
    )
    main_rs = (
        "fn main() {\n"
        "    let mut buf = itoa::Buffer::new();\n"
        "    let _ = buf.format(42i32);\n"
        '    print!("TOUR");\n'
        "    for i in 1..=42 {\n"
        '        print!(" {}", i);\n'
        "    }\n"
        '    println!();\n'
        "}\n"
    )
    files = {"Cargo.toml": cargo_toml, "src/main.rs": main_rs}
    r = ContainerRunner().run(RunSpec(preset="rust", files=files))
    assert r.status == "ok", r.stderr
    assert score_stdout(r.stdout, MATRIX).length == 699


def test_java_builds_via_proxy_then_runs_offline():
    # `mvn -q package` cannot build at all without first downloading its build plugins
    # (compiler, jar, resources, surefire, ...) from repo1.maven.org (Maven Central,
    # allowlisted) through the egress-allowlist proxy: the build container is on an
    # --internal network whose only egress is squid, so a successful build IS proof
    # the proxy permitted Maven Central. Maven honors HTTPS_PROXY for those fetches.
    # Maven's local repo defaults to $HOME/.m2 (/root/.m2), unwritable under
    # --read-only; the image redirects it (MAVEN_CONFIG + MAVEN_ARGS) to the /tmp
    # tmpfs so plugin/artifact cache writes land there. The maven-jar-plugin writes a
    # Main-Class manifest into target/app.jar (finalName=app), a thin jar with no
    # external runtime deps, so the default run_cmd `java -jar target/app.jar` runs
    # offline with --network none and prints the identity tour (1..42), length 699.
    pom = (
        '<project xmlns="http://maven.apache.org/POM/4.0.0">\n'
        "  <modelVersion>4.0.0</modelVersion>\n"
        "  <groupId>arena</groupId>\n"
        "  <artifactId>solver</artifactId>\n"
        "  <version>1.0</version>\n"
        "  <packaging>jar</packaging>\n"
        "  <properties>\n"
        "    <maven.compiler.release>21</maven.compiler.release>\n"
        "    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>\n"
        "  </properties>\n"
        "  <build>\n"
        "    <finalName>app</finalName>\n"
        "    <plugins>\n"
        "      <plugin>\n"
        "        <groupId>org.apache.maven.plugins</groupId>\n"
        "        <artifactId>maven-jar-plugin</artifactId>\n"
        "        <configuration>\n"
        "          <archive><manifest><mainClass>Main</mainClass></manifest></archive>\n"
        "        </configuration>\n"
        "      </plugin>\n"
        "    </plugins>\n"
        "  </build>\n"
        "</project>\n"
    )
    main_java = (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        '        StringBuilder sb = new StringBuilder("TOUR");\n'
        "        for (int i = 1; i <= 42; i++) sb.append(\" \").append(i);\n"
        "        System.out.println(sb.toString());\n"
        "    }\n"
        "}\n"
    )
    files = {"pom.xml": pom, "src/main/java/Main.java": main_java}
    r = ContainerRunner().run(RunSpec(preset="java", files=files))
    assert r.status == "ok", r.stderr
    assert score_stdout(r.stdout, MATRIX).length == 699
