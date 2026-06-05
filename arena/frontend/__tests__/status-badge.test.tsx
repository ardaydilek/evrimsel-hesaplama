import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatusBadge } from "@/components/status-badge";

describe("StatusBadge", () => {
  it.each([
    ["queued", "Sırada"],
    ["running", "Çalışıyor"],
    ["scored", "Puanlandı"],
    ["failed", "Başarısız"],
  ] as const)("renders %s as %s", (status, label) => {
    render(<StatusBadge status={status} />);
    expect(screen.getByTestId("status-badge")).toHaveTextContent(label);
  });
});
