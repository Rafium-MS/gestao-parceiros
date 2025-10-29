import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Button } from "../Button";
import styles from "../Button.module.css";

describe("Button", () => {
  it("renders the provided label", () => {
    render(<Button>Salvar</Button>);

    expect(screen.getByRole("button", { name: "Salvar" })).toBeInTheDocument();
  });

  it("applies the secondary variant class", () => {
    render(
      <Button variant="secondary" aria-label="Ver detalhes" />
    );

    const button = screen.getByRole("button", { name: "Ver detalhes" });
    expect(button).toHaveClass(styles.variantSecondary);
  });

  it("renders a trailing icon when requested", () => {
    render(
      <Button
        icon={<span data-testid="icon" aria-hidden="true">+</span>}
        iconPosition="trailing"
      >
        Exportar
      </Button>
    );

    const button = screen.getByRole("button", { name: "Exportar" });
    const icon = screen.getByTestId("icon");

    expect(button).toContainElement(icon);
    expect(button.lastElementChild).toBe(icon);
  });

  it("applies the icon only style when no children are provided", () => {
    render(
      <Button icon={<span aria-hidden="true">+</span>} aria-label="Adicionar" />
    );

    const button = screen.getByRole("button", { name: "Adicionar" });
    expect(button).toHaveClass(styles.iconOnly);
  });
});
