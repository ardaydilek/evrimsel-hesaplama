import { describe, it, expect } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { MultiFileEditor, filesToMap, type FileEntry } from "@/components/multi-file-editor";

function Harness() {
  const [files, setFiles] = useState<FileEntry[]>([{ path: "main.py", content: "print(1)" }]);
  return (
    <>
      <MultiFileEditor files={files} onChange={setFiles} />
      <pre data-testid="dump">{JSON.stringify(filesToMap(files))}</pre>
    </>
  );
}

const dump = () => JSON.parse(screen.getByTestId("dump").textContent!);

describe("filesToMap", () => {
  it("builds a path->content map and drops empty paths", () => {
    expect(
      filesToMap([
        { path: "main.py", content: "a" },
        { path: "  ", content: "ignored" },
      ]),
    ).toEqual({ "main.py": "a" });
  });
});

describe("MultiFileEditor", () => {
  it("adds a file via the + tab, edits the active file, and switches between tabs", async () => {
    const user = userEvent.setup();
    render(<Harness />);

    // Only the active file is shown — a single path/content pair.
    expect(screen.getAllByLabelText(/dosya yolu/i)).toHaveLength(1);

    // The + button appends a file and focuses it as the active tab.
    await user.click(screen.getByRole("button", { name: /dosya ekle/i }));
    await user.type(screen.getByLabelText(/dosya yolu/i), "util.py");
    await user.type(screen.getByLabelText(/dosya içeriği/i), "x=1");
    expect(dump()).toEqual({ "main.py": "print(1)", "util.py": "x=1" });

    // Clicking the first tab switches the active file back to main.py.
    await user.click(screen.getByRole("button", { name: "main.py" }));
    expect(screen.getByLabelText(/dosya içeriği/i)).toHaveValue("print(1)");
  });

  it("removes the active tab and falls back to a neighbour", async () => {
    const user = userEvent.setup();
    render(<Harness />);
    await user.click(screen.getByRole("button", { name: /dosya ekle/i }));
    await user.type(screen.getByLabelText(/dosya yolu/i), "util.py");

    await user.click(screen.getByRole("button", { name: /dosyayı sil 1/i }));
    expect(dump()).toEqual({ "main.py": "print(1)" });
    expect(screen.getByLabelText(/dosya yolu/i)).toHaveValue("main.py");
  });

  it("accepts dropped files as new tabs", async () => {
    render(<Harness />);
    const editor = screen.getByTestId("multi-file-editor");
    const file = new File(["y=2"], "dropped.py", { type: "text/plain" });

    fireEvent.drop(editor, { dataTransfer: { files: [file] } });

    await waitFor(() =>
      expect(dump()).toEqual({ "main.py": "print(1)", "dropped.py": "y=2" }),
    );
    expect(screen.getByRole("button", { name: "dropped.py" })).toBeInTheDocument();
  });
});
