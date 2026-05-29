"""
Computer use: Claude sees a screenshot and controls mouse/keyboard.
Requires a display (or virtual framebuffer). Run in a sandboxed VM — never on production machines.
Beta feature — requires betas=["computer-use-2025-01-24"].
"""
import base64
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

# Minimal 1×1 white PNG for demo purposes — replace with real screenshot() in production
_PLACEHOLDER_PNG = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00'
    b'\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
)


def take_screenshot() -> str:
    """Return base64-encoded PNG. Replace with real implementation (e.g. pyautogui, PIL)."""
    return base64.standard_b64encode(_PLACEHOLDER_PNG).decode()


def dispatch_action(action: str, block_input: dict):
    """Execute a computer action. Replace prints with real mouse/keyboard calls."""
    if action == "screenshot":
        pass  # handled at top of loop
    elif action == "left_click":
        print(f"  [click] {block_input['coordinate']}")
    elif action == "double_click":
        print(f"  [double_click] {block_input['coordinate']}")
    elif action == "type":
        print(f"  [type] {repr(block_input['text'])}")
    elif action == "key":
        print(f"  [key] {block_input['text']}")
    elif action == "scroll":
        print(f"  [scroll] {block_input['direction']} ×{block_input['amount']} at {block_input['coordinate']}")
    elif action == "cursor_position":
        print("  [cursor_position] query")
    else:
        print(f"  [unknown action] {action}")


def run_computer_use(task: str, max_steps: int = 10):
    messages = [{"role": "user", "content": task}]
    last_tool_id = None

    for step in range(max_steps):
        screenshot_b64 = take_screenshot()

        # After step 0, inject screenshot as the tool result for the prior action
        if step > 0 and last_tool_id:
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": last_tool_id,
                    "content": [{
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/png", "data": screenshot_b64}
                    }]
                }]
            })

        response = client.beta.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            tools=[{
                "type": "computer_20250124",
                "name": "computer",
                "display_width_px": 1280,
                "display_height_px": 800,
                "display_number": 1,
            }],
            messages=messages,
            betas=["computer-use-2025-01-24"],
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            final = next((b.text for b in response.content if b.type == "text"), "")
            print(f"\nDone: {final}")
            return

        for block in response.content:
            if block.type == "tool_use" and block.name == "computer":
                last_tool_id = block.id
                action = block.input.get("action", "")
                print(f"Step {step + 1}: {action}")
                dispatch_action(action, block.input)


if __name__ == "__main__":
    print("Note: This demo uses a placeholder screenshot.")
    print("Replace take_screenshot() with a real implementation for actual use.\n")
    run_computer_use("Take a screenshot and describe what you see.")
