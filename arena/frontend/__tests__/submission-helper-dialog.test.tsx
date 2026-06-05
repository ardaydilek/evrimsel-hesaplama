import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SubmissionHelperDialog } from "@/components/submission-helper-dialog";
import { TEMPLATES } from "@/lib/solver-templates";

describe("SubmissionHelperDialog", () => {
  it("opens, shows the template + agent prompt, and supports load + copy", async () => {
    // userEvent.setup() installs a functional clipboard stub we can read back.
    const user = userEvent.setup();
    const onLoad = vi.fn();
    render(<SubmissionHelperDialog preset="python" onLoadTemplate={onLoad} />);

    await user.click(
      screen.getByRole("button", { name: /Şablon & yapay zekâ ile hazırla/i }),
    );

    // The python template source and the Turkish agent prompt are both visible.
    expect(await screen.findByText(/def main\(\)/)).toBeInTheDocument();
    expect(screen.getByText(/tek bir Python dosyasına/i)).toBeInTheDocument();

    // "Editöre yükle" hands the full template (all files) back to the editor.
    await user.click(screen.getByRole("button", { name: /Editöre yükle/i }));
    expect(onLoad).toHaveBeenCalledWith(TEMPLATES.python);

    // Re-open and copy the source; it lands in the clipboard.
    await user.click(
      screen.getByRole("button", { name: /Şablon & yapay zekâ ile hazırla/i }),
    );
    await user.click(screen.getByRole("button", { name: /Kodu kopyala/i }));
    expect(await navigator.clipboard.readText()).toBe(TEMPLATES.python[0].content);
  });
});
