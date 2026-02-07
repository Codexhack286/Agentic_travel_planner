import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChatInput } from "@/components/chat/ChatInput";

describe("ChatInput", () => {
  it("renders textarea and send button", () => {
    render(<ChatInput onSubmit={vi.fn()} isStreaming={false} />);

    expect(screen.getByLabelText("Message input")).toBeInTheDocument();
    expect(screen.getByLabelText("Send message")).toBeInTheDocument();
  });

  it("send button is disabled when input is empty", () => {
    render(<ChatInput onSubmit={vi.fn()} isStreaming={false} />);

    expect(screen.getByLabelText("Send message")).toBeDisabled();
  });

  it("calls onSubmit when Enter is pressed with content", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<ChatInput onSubmit={onSubmit} isStreaming={false} />);

    const textarea = screen.getByLabelText("Message input");
    await user.type(textarea, "Hello world{Enter}");

    expect(onSubmit).toHaveBeenCalledWith("Hello world");
  });

  it("does not submit on Shift+Enter", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<ChatInput onSubmit={onSubmit} isStreaming={false} />);

    const textarea = screen.getByLabelText("Message input");
    await user.type(textarea, "Hello{Shift>}{Enter}{/Shift}");

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("shows stop button when streaming", () => {
    render(
      <ChatInput onSubmit={vi.fn()} onStop={vi.fn()} isStreaming={true} />
    );

    expect(screen.getByLabelText("Stop generating")).toBeInTheDocument();
    expect(screen.queryByLabelText("Send message")).not.toBeInTheDocument();
  });

  it("calls onStop when stop button is clicked", async () => {
    const user = userEvent.setup();
    const onStop = vi.fn();
    render(
      <ChatInput onSubmit={vi.fn()} onStop={onStop} isStreaming={true} />
    );

    await user.click(screen.getByLabelText("Stop generating"));
    expect(onStop).toHaveBeenCalled();
  });
});
