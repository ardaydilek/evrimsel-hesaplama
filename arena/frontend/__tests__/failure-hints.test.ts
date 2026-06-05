import { describe, it, expect } from "vitest";
import { hintForFailure } from "@/lib/failure-hints";

describe("hintForFailure", () => {
  it("explains a read-only filesystem crash", () => {
    const reason =
      "terminate called ... filesystem error: cannot create directories: Read-only file system [results]";
    expect(hintForFailure(reason)).toMatch(/salt-okunur/);
  });

  it("explains a missing TOUR line", () => {
    expect(hintForFailure("no TOUR line found in output")).toMatch(/TOUR/);
  });

  it("explains a wrong city count", () => {
    expect(hintForFailure("tour has 40 cities, expected 42")).toMatch(/42 şehrin/);
  });

  it("explains a timeout", () => {
    expect(hintForFailure("execution timed out")).toMatch(/süre sınırını/);
  });

  it("returns null for unknown reasons and empty input", () => {
    expect(hintForFailure("some unrecognized compiler error")).toBeNull();
    expect(hintForFailure(null)).toBeNull();
    expect(hintForFailure("")).toBeNull();
  });
});
