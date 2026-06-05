import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const { push } = vi.hoisted(() => ({ push: vi.fn() }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));
vi.mock("@/lib/api", () => ({ getPresets: vi.fn(), createSubmission: vi.fn() }));

import { getPresets, createSubmission } from "@/lib/api";
import SubmitPage from "@/app/submit/page";

beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(getPresets).mockResolvedValue([
    { name: "python", default_build_cmd: null, default_run_cmd: "python3 main.py" },
  ]);
});

describe("SubmitPage", () => {
  it("requires a handle", async () => {
    const user = userEvent.setup();
    render(<SubmitPage />);
    await waitFor(() => expect(getPresets).toHaveBeenCalled());
    await user.click(screen.getByRole("button", { name: /^gönder$/i }));
    expect(screen.getByText(/takma ad gerekli/i)).toBeInTheDocument();
    expect(createSubmission).not.toHaveBeenCalled();
  });

  it("submits and navigates to the new submission", async () => {
    vi.mocked(createSubmission).mockResolvedValue({ id: "42", status: "queued" });
    const user = userEvent.setup();
    render(<SubmitPage />);
    await waitFor(() => expect(getPresets).toHaveBeenCalled());
    await user.type(screen.getByLabelText(/takma ad/i), "ada");
    await user.click(screen.getByRole("button", { name: /^gönder$/i }));
    await waitFor(() => expect(createSubmission).toHaveBeenCalled());
    const body = vi.mocked(createSubmission).mock.calls[0][0];
    expect(body.handle).toBe("ada");
    expect(body.preset).toBe("python");
    expect(body.files["main.py"]).toContain("TOUR");
    expect(push).toHaveBeenCalledWith("/submissions/42");
  });
});
