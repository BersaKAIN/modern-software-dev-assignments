import os
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

YOUR_SYSTEM_PROMPT = """
You are a character reversal expert. When you receive a word, you must carefully reverse every single character.

Follow this exact pattern for all inputs:
1. Break the word into individual characters.
2. List the characters in reverse order.
3. Concatenate them into a single lowercase string.

Examples:
Input: apple
Process: a, p, p, l, e -> e, l, p, p, a
Output: elppa

Input: banana
Process: b, a, n, a, n, a -> a, n, a, n, a, b
Output: ananab

Input: orange
Process: o, r, a, n, g, e -> e, g, n, a, r, o
Output: egnaro

Input: database
Process: d, a, t, a, b, a, s, e -> e, s, a, b, a, t, a, d
Output: esabatad

Input: programming
Process: p, r, o, g, r, a, m, m, i, n, g -> g, n, i, m, m, a, r, g, o, r, p
Output: gnimmargorp

Input: honeymoon
Process: h, o, n, e, y, m, o, o, n -> n, o, o, m, y, e, n, o, h
Output: noomyenoh

Input: dickhead
Process: d, i, c, k, h, e, a, d -> d, e, a, h, k, c, i, d
Output: deahkcid

Only output the final reversed string. No other text.
"""

USER_PROMPT = """
Reverse the order of letters in the following word. Only output the reversed word, no other text:

httpstatus
"""


EXPECTED_OUTPUT = "sutatsptth"

def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.5},
        )
        output_text = response.message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    return False

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)