# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import warnings
from typing import Literal, Optional, Union, Any
from google import genai
from google.genai import types
import termcolor
from google.genai.types import (
    Part,
    GenerateContentConfig,
    Content,
    Candidate,
    FunctionResponse,
    FinishReason,
)
import time
from rich.console import Console
from rich.table import Table
from loguru import logger

# Suppress AFC warning messages
warnings.filterwarnings('ignore', message='.*AFC.*')
warnings.filterwarnings('ignore', message='.*automatic function calling.*')

from computers import EnvState, Computer

MAX_RECENT_TURN_WITH_SCREENSHOTS = 3
PREDEFINED_COMPUTER_USE_FUNCTIONS = [
    "open_web_browser",
    "click_at",
    "hover_at",
    "type_text_at",
    "scroll_document",
    "scroll_at",
    "wait_5_seconds",
    "go_back",
    "go_forward",
    "search",
    "navigate",
    "key_combination",
    "drag_and_drop",
]


console = Console()

# Built-in Computer Use tools will return "EnvState".
# Custom provided functions will return "dict".
FunctionResponseT = Union[EnvState, dict]


def multiply_numbers(x: float, y: float) -> dict:
    """Multiplies two numbers."""
    return {"result": x * y}


class BrowserAgent:
    def __init__(
        self,
        browser_computer: Computer,
        query: str,
        model_name: str,
        verbose: bool = True,
    ):
        self._browser_computer = browser_computer
        self._query = query
        self._model_name = model_name
        self._verbose = verbose
        self.final_reasoning = None
        self._client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
            vertexai=os.environ.get("USE_VERTEXAI", "0").lower() in ["true", "1"],
            project=os.environ.get("VERTEXAI_PROJECT"),
            location=os.environ.get("VERTEXAI_LOCATION"),
        )
        
        # Get screen size for system prompt
        screen_width, screen_height = self._browser_computer.screen_size()
        
        # Comprehensive system prompt (inspired by Claude Computer Use)
        system_prompt = f"""You are an AI agent controlling a computer to complete user tasks.

ENVIRONMENT:
- Screen resolution: {screen_width}x{screen_height}
- You interact via mouse clicks, typing, and keyboard shortcuts
- You can take screenshots to observe the current state

IMPORTANT GUIDELINES:
1. ALWAYS take a screenshot BEFORE clicking to verify element positions
2. Click on the CENTER of elements, not edges or corners
3. Wait for applications to load - take another screenshot if needed
4. If a click fails, adjust cursor position and retry
5. After EACH action, verify it succeeded before proceeding

COMMON MISTAKES TO AVOID:
- Clicking too quickly before elements load
- Clicking on wrong coordinates
- Not verifying action success
- Repeating failed actions without adjustment

ACTION VERIFICATION:
After each action, ask yourself:
- Did the action succeed?
- Is the application/page loaded?
- Do I need to retry with different coordinates?

Your goal: {self._query}

Think step-by-step and verify each action before proceeding."""

        self._contents: list[Content] = [
            Content(
                role="user",
                parts=[
                    Part(text=system_prompt),
                ],
            )
        ]

        # Exclude any predefined functions here.
        excluded_predefined_functions = []

        # Import desktop automation functions
        # Import desktop automation functions
        from desktop_functions import DESKTOP_FUNCTION_MAP
        
        # Store desktop function map for execution
        self._desktop_function_map = DESKTOP_FUNCTION_MAP

        # Add your own custom functions here.
        custom_functions = [
            types.FunctionDeclaration.from_callable(client=self._client, callable=func)
            for func in DESKTOP_FUNCTION_MAP.values()
        ] + [
            # Example math function
            types.FunctionDeclaration.from_callable(
                client=self._client, callable=multiply_numbers
            )
        ]

        self._generate_content_config = GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            tools=[
                types.Tool(
                    computer_use=types.ComputerUse(
                        environment=types.Environment.ENVIRONMENT_BROWSER,
                        excluded_predefined_functions=excluded_predefined_functions,
                    ),
                ),
                types.Tool(function_declarations=custom_functions),
            ],
        )
        
        # Track actions for completion detection
        self._action_history = []
        self._iteration_count = 0
        self._max_iterations = 30  # Safety limit
        
        # Hierarchical planning state
        self._current_plan = []  # Queue of planned actions
        self._plan_context = ""  # Context from last planning session
        
        # Action retry tracking (inspired by Claude)
        self._last_action = None
        self._last_action_retry_count = 0
        self._max_retries_per_action = 2

    def create_action_plan(self, current_state: str) -> list[dict]:
        """Create a multi-step action plan using Gemini Flash.
        
        Returns:
            List of planned actions with reasoning
        """
        try:
            planning_prompt = f"""
You are planning actions for: {self._query}

Current state: {current_state}
Actions taken so far: {len(self._action_history)}

Create a plan of 3-5 specific actions to make progress. For each action:
1. What to do (click, type, scroll, etc.)
2. Why this action helps
3. What element to interact with

Format as JSON array:
[
  {{"action": "click", "target": "element description", "reason": "why"}},
  {{"action": "type", "text": "what to type", "target": "where", "reason": "why"}},
  ...
]

Be specific and actionable. Focus on the NEXT steps, not the entire task.
"""
            
            response = self._client.models.generate_content(
                model='gemini-2.0-flash-exp',  # Fast model for planning
                contents=planning_prompt
            )
            
            import json
            import re
            
            # Extract JSON from response
            text = response.text.strip()
            # Find JSON array in the response
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                console.print(f"[cyan]📋 Created plan with {len(plan)} steps[/cyan]")
                return plan
            else:
                logger.warning("Could not parse plan from response")
                return []
                
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return []

    def should_take_screenshot(self, action_name: str) -> bool:
        """Determine if we need a screenshot after this action.
        
        Skip screenshots for actions that don't change visual state much.
        """
        # Always screenshot for these (they change what's visible)
        visual_actions = {
            'click', 'click_at', 'navigate', 'scroll', 'scroll_at',
            'scroll_document', 'go_back', 'go_forward', 'open_app',
            'drag_and_drop'
        }
        
        # Skip screenshots for these (minimal visual change)
        non_visual_actions = {
            'type_text', 'type_text_at', 'key_combination',
            'wait_5_seconds', 'hotkey', 'execute_applescript'
        }
        
        if action_name in visual_actions:
            return True
        elif action_name in non_visual_actions:
            # Take screenshot every 3 non-visual actions to stay updated
            non_visual_count = sum(
                1 for a in self._action_history[-3:]
                if a['name'] in non_visual_actions
            )
            return non_visual_count >= 2
        
        # Default: take screenshot (be safe)
        return True

    def evaluate_action_success(self, action_name: str, action_args: dict) -> tuple[bool, str]:
        """Evaluate if the last action succeeded using Gemini Flash.
        
        Returns:
            (success: bool, feedback: str)
        """
        try:
            # Get recent context
            recent_actions = self._action_history[-3:] if len(self._action_history) >= 3 else self._action_history
            
            eval_prompt = f"""You just performed this action:
Action: {action_name}
Arguments: {action_args}

Recent action history: {recent_actions}

Based on the current screenshot and context, did this action succeed?

Answer with ONLY:
SUCCESS - if the action clearly worked as intended
FAILED - if the action clearly failed or had no effect
UNCERTAIN - if you can't tell yet (need to wait/observe more)

Then briefly explain why (one sentence).

Format: STATUS: explanation"""

            response = self._client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=eval_prompt
            )
            
            result_text = response.text.strip().upper()
            
            if "SUCCESS" in result_text:
                return True, result_text
            elif "FAILED" in result_text:
                return False, result_text
            else:  # UNCERTAIN
                return True, result_text  # Assume success if uncertain
                
        except Exception as e:
            logger.error(f"Action evaluation failed: {e}")
            return True, "Evaluation failed, assuming success"


    def check_if_task_complete(self) -> bool:
        """Check if the task is complete based on actions taken."""
        if not self._action_history:
            return False
        
        # Don't check completion too early
        if len(self._action_history) < 2:
            return False
        
        try:
            # Build action summary
            recent_actions = self._action_history[-5:]  # Last 5 actions
            action_summary = "\n".join([
                f"- {a['name']}: {a.get('args', {})}" 
                for a in recent_actions
            ])
            
            completion_prompt = f"""
Original task: {self._query}

Actions taken:
{action_summary}

Is this task COMPLETE? Consider:
- For writing tasks: Has the text been written/typed?
- For navigation tasks: Have we reached the destination?
- For search tasks: Have we found and displayed results?

Respond with ONLY "YES" or "NO".
"""
            
            response = self._client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=completion_prompt
            )
            
            result = response.text.strip().upper()
            return "YES" in result
            
        except Exception as e:
            logger.error(f"Completion check failed: {e}")
            return False

    def detect_repetitive_actions(self) -> tuple[bool, str]:
        """Detect if agent is stuck in a loop and suggest alternatives.
        
        Returns:
            (is_looping, suggestion) tuple
        """
        if len(self._action_history) < 4:
            return False, ""
        
        # Check last 4 actions for repetition
        recent_actions = self._action_history[-4:]
        action_names = [a['name'] for a in recent_actions]
        
        # Detect exact repetition (same action 3+ times)
        if len(set(action_names)) == 1:
            repeated_action = action_names[0]
            console.print(f"[yellow]⚠️ Detected loop: Repeating '{repeated_action}' action[/yellow]")
            
            suggestion = f"""
You've been repeating the same action '{repeated_action}' multiple times.
This suggests the current approach isn't working. Consider:
1. Is the element you're targeting actually visible/clickable?
2. Do you need to wait for something to load first?
3. Should you try a different approach entirely?
4. Is the task already complete?

Try a DIFFERENT action or mark the task as DONE/FAIL.
"""
            return True, suggestion
        
        # Detect alternating pattern (A-B-A-B)
        if len(recent_actions) >= 4:
            if (action_names[0] == action_names[2] and 
                action_names[1] == action_names[3] and
                action_names[0] != action_names[1]):
                console.print(f"[yellow]⚠️ Detected loop: Alternating between '{action_names[0]}' and '{action_names[1]}'[/yellow]")
                
                suggestion = f"""
You're alternating between '{action_names[0]}' and '{action_names[1]}'.
This pattern suggests you're stuck. Consider:
1. Is there a prerequisite step you're missing?
2. Do you need to interact with a different element first?
3. Should you try a completely different strategy?

Break the pattern with a NEW action.
"""
                return True, suggestion
        
        return False, ""


    def handle_action(self, action: types.FunctionCall) -> FunctionResponseT:
        """Handles the action and returns the environment state."""
        if action.name == "open_web_browser":
            return self._browser_computer.open_web_browser()
        elif action.name == "click_at":
            x = self.denormalize_x(action.args["x"])
            y = self.denormalize_y(action.args["y"])
            return self._browser_computer.click_at(
                x=x,
                y=y,
            )
        elif action.name == "hover_at":
            x = self.denormalize_x(action.args["x"])
            y = self.denormalize_y(action.args["y"])
            return self._browser_computer.hover_at(
                x=x,
                y=y,
            )
        elif action.name == "type_text_at":
            x = self.denormalize_x(action.args["x"])
            y = self.denormalize_y(action.args["y"])
            press_enter = action.args.get("press_enter", False)
            clear_before_typing = action.args.get("clear_before_typing", True)
            return self._browser_computer.type_text_at(
                x=x,
                y=y,
                text=action.args["text"],
                press_enter=press_enter,
                clear_before_typing=clear_before_typing,
            )
        elif action.name == "scroll_document":
            return self._browser_computer.scroll_document(action.args["direction"])
        elif action.name == "scroll_at":
            x = self.denormalize_x(action.args["x"])
            y = self.denormalize_y(action.args["y"])
            magnitude = action.args.get("magnitude", 800)
            direction = action.args["direction"]

            if direction in ("up", "down"):
                magnitude = self.denormalize_y(magnitude)
            elif direction in ("left", "right"):
                magnitude = self.denormalize_x(magnitude)
            else:
                raise ValueError("Unknown direction: ", direction)
            return self._browser_computer.scroll_at(
                x=x, y=y, direction=direction, magnitude=magnitude
            )
        elif action.name == "wait_5_seconds":
            return self._browser_computer.wait_5_seconds()
        elif action.name == "go_back":
            return self._browser_computer.go_back()
        elif action.name == "go_forward":
            return self._browser_computer.go_forward()
        elif action.name == "search":
            return self._browser_computer.search()
        elif action.name == "navigate":
            return self._browser_computer.navigate(action.args["url"])
        elif action.name == "key_combination":
            return self._browser_computer.key_combination(
                action.args["keys"].split("+")
            )
        elif action.name == "drag_and_drop":
            x = self.denormalize_x(action.args["x"])
            y = self.denormalize_y(action.args["y"])
            destination_x = self.denormalize_x(action.args["destination_x"])
            destination_y = self.denormalize_y(action.args["destination_y"])
            return self._browser_computer.drag_and_drop(
                x=x,
                y=y,
                destination_x=destination_x,
                destination_y=destination_y,
            )
        # Handle the custom function declarations here.
        elif action.name == multiply_numbers.__name__:
            return multiply_numbers(x=action.args["x"], y=action.args["y"])
        # Handle desktop automation functions
        elif action.name in self._desktop_function_map:
            console.print(f"[yellow]🖥️  Desktop action: {action.name}[/yellow]")
            func = self._desktop_function_map[action.name]
            # Filter out safety_decision - it's handled separately
            clean_args = {k: v for k, v in action.args.items() if k != 'safety_decision'}
            result = func(**clean_args)
            console.print(f"[green]✅ Result: {result}[/green]")
            return result
        else:
            raise ValueError(f"Unsupported function: {action}")

    def get_model_response(
        self, max_retries=5, base_delay_s=1
    ) -> types.GenerateContentResponse:
        for attempt in range(max_retries):
            try:
                response = self._client.models.generate_content(
                    model=self._model_name,
                    contents=self._contents,
                    config=self._generate_content_config,
                )
                return response  # Return response on success
            except Exception as e:
                print(e)
                if attempt < max_retries - 1:
                    delay = base_delay_s * (2**attempt)
                    message = (
                        f"Generating content failed on attempt {attempt + 1}. "
                        f"Retrying in {delay} seconds...\n"
                    )
                    termcolor.cprint(
                        message,
                        color="yellow",
                    )
                    time.sleep(delay)
                else:
                    termcolor.cprint(
                        f"Generating content failed after {max_retries} attempts.\n",
                        color="red",
                    )
                    raise

    def get_text(self, candidate: Candidate) -> Optional[str]:
        """Extracts the text from the candidate."""
        if not candidate.content or not candidate.content.parts:
            return None
        text = []
        for part in candidate.content.parts:
            if part.text:
                text.append(part.text)
        return " ".join(text) or None

    def extract_function_calls(self, candidate: Candidate) -> list[types.FunctionCall]:
        """Extracts the function call from the candidate."""
        if not candidate.content or not candidate.content.parts:
            return []
        ret = []
        for part in candidate.content.parts:
            if part.function_call:
                ret.append(part.function_call)
        return ret

    def run_one_iteration(self) -> Literal["COMPLETE", "CONTINUE"]:
        # Check for repetitive actions (trajectory reflection)
        is_looping, reflection_msg = self.detect_repetitive_actions()
        if is_looping:
            # Add reflection as a user message to guide the model
            self._contents.append(
                Content(
                    role="user",
                    parts=[Part(text=f"REFLECTION: {reflection_msg}")]
                )
            )
            # Clear plan if we're looping - need to replan
            self._current_plan = []
        
        # Create a new plan if we don't have one (every ~5 iterations)
        if not self._current_plan and self._iteration_count % 5 == 0:
            current_state_desc = f"Iteration {self._iteration_count}, last action: {self._action_history[-1]['name'] if self._action_history else 'none'}"
            self._current_plan = self.create_action_plan(current_state_desc)
            
            # Add plan as guidance to the model
            if self._current_plan:
                plan_text = "PLAN:\n" + "\n".join([
                    f"{i+1}. {step['action']} - {step.get('reason', 'N/A')}"
                    for i, step in enumerate(self._current_plan[:3])  # Show first 3 steps
                ])
                self._contents.append(
                    Content(
                        role="user",
                        parts=[Part(text=plan_text)]
                    )
                )
        
        
        # Generate a response from the model.
        if self._verbose:
            with console.status(
                "Generating response from Gemini Computer Use...", spinner_style=None
            ):
                try:
                    response = self.get_model_response()
                except Exception as e:
                    return "COMPLETE"
        else:
            try:
                response = self.get_model_response()
            except Exception as e:
                return "COMPLETE"

        if not response.candidates:
            termcolor.cprint("⚠️  Response was empty! This might be due to a Captcha or Safety Block.", "red", attrs=["bold"])
            print(response.prompt_feedback)
            
            # Manual Recovery
            termcolor.cprint("\n🛑 PAUSED: Please check the browser window.", "yellow")
            termcolor.cprint("1. Solve any Captchas manually.", "yellow")
            termcolor.cprint("2. If the page is blank/stuck, refresh it.", "yellow")
            input(termcolor.colored("Press [Enter] when you are ready to continue...", "green", attrs=["bold"]))
            
            # Refresh Screenshot
            print("📸 Refreshing view...")
            new_state = self._browser_computer.current_state()
            
            # Update the last user message with the new screenshot
            if self._contents and self._contents[-1].role == "user":
                last_content = self._contents[-1]
                for part in last_content.parts:
                    if part.function_response and part.function_response.parts:
                        # Update the image data
                        part.function_response.parts[0].inline_data.data = new_state.screenshot
                        # Update URL if changed
                        if "url" in part.function_response.response:
                            part.function_response.response["url"] = new_state.url
            
            print("🔄 Retrying...")
            return self.run_one_iteration()

        # Extract the text and function call from the response.
        candidate = response.candidates[0]
        # Append the model turn to conversation history.
        if candidate.content:
            self._contents.append(candidate.content)

        reasoning = self.get_text(candidate)
        function_calls = self.extract_function_calls(candidate)

        # Retry the request in case of malformed FCs.
        if (
            not function_calls
            and not reasoning
            and candidate.finish_reason == FinishReason.MALFORMED_FUNCTION_CALL
        ):
            return "CONTINUE"

        if not function_calls:
            print(f"Agent Loop Complete: {reasoning}")
            self.final_reasoning = reasoning
            return "COMPLETE"

        function_call_strs = []
        for function_call in function_calls:
            # Print the function call and any reasoning.
            function_call_str = f"Name: {function_call.name}"
            if function_call.args:
                function_call_str += f"\nArgs:"
                for key, value in function_call.args.items():
                    function_call_str += f"\n  {key}: {value}"
            function_call_strs.append(function_call_str)

        table = Table(expand=True)
        table.add_column(
            "Gemini Computer Use Reasoning", header_style="magenta", ratio=1
        )
        table.add_column("Function Call(s)", header_style="cyan", ratio=1)
        table.add_row(reasoning, "\n".join(function_call_strs))
        if self._verbose:
            console.print(table)
            print()

        function_responses = []
        for function_call in function_calls:
            extra_fr_fields = {}
            if function_call.args and (
                safety := function_call.args.get("safety_decision")
            ):
                decision = self._get_safety_confirmation(safety)
                if decision == "TERMINATE":
                    print("Terminating agent loop")
                    return "COMPLETE"
                # Explicitly mark the safety check as acknowledged.
                extra_fr_fields["safety_acknowledgement"] = "true"
            if self._verbose:
                with console.status(
                    "Sending command to Computer...", spinner_style=None
                ):
                    fc_result = self.handle_action(function_call)
            else:
                fc_result = self.handle_action(function_call)
            if isinstance(fc_result, EnvState):
                function_responses.append(
                    FunctionResponse(
                        name=function_call.name,
                        response={
                            "url": fc_result.url,
                            **extra_fr_fields,
                        },
                        parts=[
                            types.FunctionResponsePart(
                                inline_data=types.FunctionResponseBlob(
                                    mime_type="image/png", data=fc_result.screenshot
                                )
                            )
                        ],
                    )
                )
            elif isinstance(fc_result, dict):
                # Merge extra fields (like safety_acknowledgement) into the result
                response_data = {**fc_result, **extra_fr_fields}
                function_responses.append(
                    FunctionResponse(name=function_call.name, response=response_data)
                )

        self._contents.append(
            Content(
                role="user",
                parts=[Part(function_response=fr) for fr in function_responses],
            )
        )

        # only keep screenshots in the few most recent turns, remove the screenshot images from the old turns.
        turn_with_screenshots_found = 0
        for content in reversed(self._contents):
            if content.role == "user" and content.parts:
                # check if content has screenshot of the predefined computer use functions.
                has_screenshot = False
                for part in content.parts:
                    if (
                        part.function_response
                        and part.function_response.parts
                        and part.function_response.name
                        in PREDEFINED_COMPUTER_USE_FUNCTIONS
                    ):
                        has_screenshot = True
                        break

                if has_screenshot:
                    turn_with_screenshots_found += 1
                    # remove the screenshot image if the number of screenshots exceed the limit.
                    if turn_with_screenshots_found > MAX_RECENT_TURN_WITH_SCREENSHOTS:
                        for part in content.parts:
                            if (
                                part.function_response
                                and part.function_response.parts
                                and part.function_response.name
                                in PREDEFINED_COMPUTER_USE_FUNCTIONS
                            ):
                                part.function_response.parts = None

        # Track actions for completion detection
        for function_call in function_calls:
            self._action_history.append({
                'name': function_call.name,
                'args': dict(function_call.args) if function_call.args else {}
            })
        
        # Self-evaluate the last action (inspired by Claude)
        if function_calls and len(function_calls) > 0:
            last_call = function_calls[-1]
            action_name = last_call.name
            action_args = dict(last_call.args) if last_call.args else {}
            
            # Check if this is a retry of the same action
            if self._last_action == (action_name, str(action_args)):
                self._last_action_retry_count += 1
            else:
                self._last_action = (action_name, str(action_args))
                self._last_action_retry_count = 0
            
            # Evaluate action success (skip for screenshot actions)
            if action_name not in ['screenshot', 'cursor_position']:
                success, feedback = self.evaluate_action_success(action_name, action_args)
                
                if not success and self._last_action_retry_count < self._max_retries_per_action:
                    console.print(f"[yellow]⚠️ Action failed: {feedback}[/yellow]")
                    console.print(f"[yellow]🔄 Retry {self._last_action_retry_count + 1}/{self._max_retries_per_action}[/yellow]")
                    
                    # Add retry guidance to the model
                    retry_msg = f"""
RETRY NEEDED: The last action '{action_name}' failed.
Feedback: {feedback}

Suggestions:
1. Try clicking a slightly different position (adjust coordinates)
2. Wait a moment for the element to load
3. Take a screenshot to verify the element is visible
4. Try a different approach if this keeps failing

Please retry with adjustments."""
                    
                    self._contents.append(
                        Content(
                            role="user",
                            parts=[Part(text=retry_msg)]
                        )
                    )
                elif not success:
                    console.print(f"[red]❌ Action failed after {self._max_retries_per_action} retries[/red]")
                    # Reset retry counter and continue
                    self._last_action_retry_count = 0
                else:
                    console.print(f"[green]✓ Action succeeded: {action_name}[/green]")
        
        # Increment iteration counter
        self._iteration_count += 1
        
        # Check if we've hit the iteration limit
        if self._iteration_count >= self._max_iterations:
            console.print("[yellow]⚠️ Reached maximum iterations. Stopping.[/yellow]")
            return "COMPLETE"
        
        # Check if task is complete (every 3 iterations to save API calls)
        if self._iteration_count % 3 == 0 and self._iteration_count > 3:
            if self.check_if_task_complete():
                console.print("[green]✅ Task appears to be complete![/green]")
                return "COMPLETE"

        return "CONTINUE"

    def _get_safety_confirmation(
        self, safety: dict[str, Any]
    ) -> Literal["CONTINUE", "TERMINATE"]:
        if safety["decision"] != "require_confirmation":
            raise ValueError(f"Unknown safety decision: safety['decision']")
        
        # Import rich for beautiful formatting
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        
        console = Console()
        
        # Create beautiful alert message
        alert_text = Text()
        alert_text.append("🤖 CAPTCHA Detected!\n\n", style="bold yellow")
        alert_text.append(safety["explanation"] + "\n\n", style="white")
        alert_text.append("Press ", style="dim")
        alert_text.append("ENTER", style="bold green")
        alert_text.append(" to let me continue, or type ", style="dim")
        alert_text.append("'no'", style="bold red")
        alert_text.append(" to stop.", style="dim")
        
        console.print(Panel(
            alert_text,
            title="[bold yellow]⚠️  Human Confirmation Required[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        ))
        
        decision = input("\n> ")
        if decision.lower() in ("n", "no"):
            console.print("[red]❌ Stopped by user[/red]")
            return "TERMINATE"
        console.print("[green]✅ Continuing...[/green]")
        return "CONTINUE"

    def agent_loop(self):
        status = "CONTINUE"
        while status == "CONTINUE":
            status = self.run_one_iteration()

    def denormalize_x(self, x: int) -> int:
        return int(x / 1000 * self._browser_computer.screen_size()[0])

    def denormalize_y(self, y: int) -> int:
        return int(y / 1000 * self._browser_computer.screen_size()[1])
