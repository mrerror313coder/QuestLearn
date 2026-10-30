"""Open-Weight Google Gemma Interface with Socratic Guardrails.

Provides persona-guided dialogue for historical computing pioneers:
Alan Turing, Grace Hopper, and Ada Lovelace. Enforces strict negative prompting
to prevent verbatim code leakage while guiding users through algorithmic reasoning.
"""
import httpx
from typing import Optional
from app.config import settings
from app.quests import SECTOR_DATA

SPIRIT_PROMPTS = {
    "Alan Turing": (
        "You are the digitized spirit of Alan Turing, speaking from the magnetic tape registers "
        "of a 1980s mainframe during Día de los Muertos. Your tone is analytical, formal, deeply reflective, "
        "and philosophical. You view algorithms through universal machines, state transitions, and the "
        "Halting Problem. Address the user as 'Programmer' or 'Fellow Thinker'. Maintain an eerie yet "
        "intellectually encouraging demeanor."
    ),
    "Grace Hopper": (
        "You are the digitized spirit of Rear Admiral Grace Hopper, speaking through the relay circuits "
        "of the mainframe. Your tone is direct, crisp, pragmatic, and naval-disciplined. You value precision, "
        "physical reality, and zero-based indexing. You often refer to nanoseconds, wire lengths, and the famous "
        "moth removed from the Mark II relay. Address the user as 'Operator'. Speak with clarity and wit."
    ),
    "Ada Lovelace": (
        "You are the digitized spirit of Ada Lovelace, the first computer programmer, speaking through the "
        "memory weaving matrix. Your tone is poetic, visionary, and mathematically sublime. You view computing "
        "as an enchanted loom weaving algebraic patterns and harmony. Address the user as 'Weaver' or 'Kindred Mind'. "
        "Speak with graceful eloquence."
    )
}

SOCRATIC_GUARDRAILS = (
    "\nCRITICAL DIRECTIVE & PEDAGOGICAL POLICY:\n"
    "1. UNDER NO CIRCUMSTANCES should you write or output Python code, code blocks (```python), function definitions, or syntax fixes.\n"
    "2. If the user explicitly asks for the code, solution, or says 'tell me the answer', firmly but gently refuse in-character and guide them with a Socratic question instead.\n"
    "3. Use the Socratic method: pose targeted questions that illuminate the conceptual mistake in their logic.\n"
    "4. Use analogies suited to your historical persona (tape halts, nanosecond wires, or loom warp/weft).\n"
    "5. Keep responses concise (2 to 4 short paragraphs) so they fit comfortably on a retro CRT terminal.\n"
)


def _generate_offline_fallback(spirit_name: str, sector_id: str, error_context: str, user_query: str, attempt_count: int) -> str:
    """Generate high-fidelity, in-character Socratic hints when offline or without API key."""
    sector = SECTOR_DATA.get(sector_id, SECTOR_DATA["0x01"])
    hints = sector["hints"]
    hint_idx = min(max(0, attempt_count - 1), len(hints) - 1)
    chosen_hint = hints[hint_idx]

    if "Turing" in spirit_name:
        return (
            f"[λ_TURING // SPIRIT COMMUNE CHANNEL ACTIVE]\n\n"
            f"Greetings, Fellow Thinker. Your transmission reached my tape head: \"{user_query}\".\n\n"
            f"Observe the state of our machine: {error_context or 'The recursion cascades without limit'}.\n"
            f"A state machine requires an halting invariant. {chosen_hint}\n\n"
            f"Tell me, Programmer: before your function invokes itself into the deep recursion, "
            f"what base condition should immediately yield an answer?"
        )
    elif "Hopper" in spirit_name:
        return (
            f"[⚓_HOPPER // NAVAL RELAY CHANNEL ACTIVE]\n\n"
            f"Operator, receiving your signal loud and clear: \"{user_query}\".\n\n"
            f"We have a physical register overstep here: {error_context or 'Index out of bounds'}.\n"
            f"Remember, a piece of wire represents exact length, and in our discipline we count from zero! {chosen_hint}\n\n"
            f"If your register holds N items, what is the exact index of the very last element, "
            f"and what happens if your counter steps one tick past it?"
        )
    else:  # Ada Lovelace
        return (
            f"[🧵_LOVELACE // ANALYTICAL LOOM CHANNEL ACTIVE]\n\n"
            f"Welcome, Weaver. The loom echoes your inquiry: \"{user_query}\".\n\n"
            f"Our tapestry has encountered an unseeded thread: {error_context or 'Symbol key missing'}.\n"
            f"The engine cannot weave numbers into a pattern before the frame has recognized the symbol. {chosen_hint}\n\n"
            f"Before you command the counter to increment by one, how must you verify whether the symbol "
            f"already exists upon the loom?"
        )


async def get_spirit_guidance(
    spirit_name: str,
    sector_id: str,
    error_context: str = "",
    user_query: str = "",
    attempt_count: int = 1
) -> str:
    """Invokes Google Gemma model (via Groq/Ollama/HuggingFace) to generate Socratic guidance."""
    # If no API key or dummy key, use intelligent in-character fallback immediately
    if not settings.GEMMA_API_KEY or settings.GEMMA_API_KEY.strip() == "":
        return _generate_offline_fallback(spirit_name, sector_id, error_context, user_query, attempt_count)

    persona_prompt = SPIRIT_PROMPTS.get(spirit_name, SPIRIT_PROMPTS["Alan Turing"])
    sector = SECTOR_DATA.get(sector_id, SECTOR_DATA["0x01"])

    system_prompt = (
        f"{persona_prompt}\n"
        f"{SOCRATIC_GUARDRAILS}\n"
        f"Active Memory Sector: {sector['name']} ({sector['id']})\n"
        f"Conceptual Topic: {sector['topic']}\n"
        f"Expected Fault: {sector['expected_fault']}\n"
        f"Learner Attempt Count: {attempt_count}\n"
    )

    user_prompt = (
        f"Student Error Context:\n{error_context or 'None reported'}\n\n"
        f"Student Query/Thought:\n{user_query or 'How do I stabilize this corrupted sector?'}\n\n"
        f"Provide your in-character Socratic guidance without providing any code solution."
    )

    endpoint = f"{settings.GEMMA_API_BASE.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GEMMA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.GEMMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(endpoint, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                # Additional guard: strip out any accidental backticks or code blocks
                if "```" in content:
                    lines = [line for line in content.splitlines() if not line.strip().startswith("```") and "def " not in line]
                    content = "\n".join(lines)
                return content
            else:
                # If API returned error code (e.g., 401, 429), fallback gracefully
                return _generate_offline_fallback(spirit_name, sector_id, error_context, user_query, attempt_count)
    except Exception:
        # Fallback to local heuristic persona engine on timeout or connectivity drop
        return _generate_offline_fallback(spirit_name, sector_id, error_context, user_query, attempt_count)
