"""FastAPI application entry point for QuestLearn: Shadows of the Machine.

Orchestrates the presentation, sandbox execution, Socratic guidance,
and data persistence layers.
"""
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, Field

from app.config import settings
from app.database import (
    init_db,
    get_or_create_session,
    update_session_patch,
    record_commune_log,
    switch_session_sector,
    reset_session
)
from app.quests import SECTOR_DATA
from app.sandbox import execute_user_patch
from app.llm_engine import get_spirit_guidance


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables or Mongo connection
    await init_db()
    yield


app = FastAPI(
    title="QuestLearn: Shadows of the Machine",
    description="Retro terminal RPG for narrative debugging with open-weight Gemma Socratic mentors.",
    version="1.0.0",
    lifespan=lifespan
)

# Static directory mount
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Pydantic Request Models
class PatchRequest(BaseModel):
    session_id: str = Field(..., description="Unique terminal session ID")
    sector_id: str = Field(..., description="Target memory sector ID (e.g. 0x01)")
    code: str = Field(..., description="Candidate Python code to patch the subroutine")


class CommuneRequest(BaseModel):
    session_id: str = Field(..., description="Unique terminal session ID")
    sector_id: str = Field(..., description="Target memory sector ID")
    message: str = Field(..., description="Player question or thought to historical spirit")
    error_context: Optional[str] = Field("", description="Latest execution traceback or error message")


class SwitchSectorRequest(BaseModel):
    session_id: str
    sector_id: str


class ResetRequest(BaseModel):
    session_id: str


@app.get("/")
async def serve_index():
    """Serves the main phosphor-green CRT terminal interface."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Terminal UI not built.")
    return FileResponse(str(index_file))


@app.get("/api/health")
async def health_check():
    """Health check endpoint for Render deployment."""
    return {
        "status": "online",
        "system": "AetherOS Mainframe v2.41",
        "gemma_model": settings.GEMMA_MODEL,
        "api_base": settings.GEMMA_API_BASE
    }


@app.get("/api/sector/{sector_id}")
async def get_sector(sector_id: str):
    """Retrieves corrupted code, lore, and metadata for a specific sector."""
    if sector_id not in SECTOR_DATA:
        raise HTTPException(status_code=404, detail=f"Memory sector {sector_id} not mapped in kernel.")
    sector = SECTOR_DATA[sector_id]
    return {
        "id": sector["id"],
        "name": sector["name"],
        "alias": sector["alias"],
        "topic": sector["topic"],
        "spirit_name": sector["spirit_name"],
        "spirit_title": sector["spirit_title"],
        "spirit_avatar": sector["spirit_avatar"],
        "lore": sector["lore"],
        "corrupted_code": sector["corrupted_code"],
        "sample_input": sector["sample_input"],
        "expected_fault": sector["expected_fault"],
        "stack_trace_demo": sector["stack_trace_demo"],
        "default_spirit_quote": sector["default_spirit_quote"]
    }


@app.get("/api/sectors")
async def list_sectors():
    """Lists all sectors in the memory bank."""
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "topic": s["topic"],
            "spirit_name": s["spirit_name"]
        }
        for s in SECTOR_DATA.values()
    ]


@app.get("/api/inspect/{sector_id}")
async def inspect_sector(sector_id: str):
    """Returns simulated runtime heap, call stack, or register states."""
    if sector_id not in SECTOR_DATA:
        raise HTTPException(status_code=404, detail=f"Sector {sector_id} not found.")
    return {
        "sector_id": sector_id,
        "inspect_data": SECTOR_DATA[sector_id]["inspect_data"]
    }


@app.get("/api/status/{session_id}")
async def get_status(session_id: str):
    """Returns current system integrity percentage, solved sectors, and attempt counts."""
    session = await get_or_create_session(session_id)
    return {
        "session_id": session["session_id"],
        "current_sector": session["current_sector"],
        "integrity_score": session["integrity_score"],
        "solved_sectors": session["solved_sectors"],
        "attempts": session["attempts"],
        "exorcism_achieved": session["integrity_score"] >= 100
    }


@app.post("/api/patch")
async def apply_patch(payload: PatchRequest):
    """Executes player-submitted patch in the isolated sandbox harness."""
    if payload.sector_id not in SECTOR_DATA:
        raise HTTPException(status_code=404, detail=f"Sector {payload.sector_id} not found.")

    sector = SECTOR_DATA[payload.sector_id]
    test_assertions = sector["test_assertions"]

    # Execute inside subprocess sandbox
    exec_result = execute_user_patch(payload.code, test_assertions)
    passed = exec_result["success"]

    # Persist in session database
    updated_session = await update_session_patch(
        session_id=payload.session_id,
        sector_id=payload.sector_id,
        passed=passed,
        code=payload.code,
        error_msg=exec_result.get("error_message", "")
    )

    return {
        "success": passed,
        "sector_id": payload.sector_id,
        "output": exec_result["output"],
        "error_type": exec_result.get("error_type"),
        "error_message": exec_result.get("error_message"),
        "session": updated_session,
        "exorcism_achieved": updated_session["integrity_score"] >= 100
    }


@app.post("/api/commune")
async def commune_with_spirit(payload: CommuneRequest):
    """Routes student inquiry to the sector's historical spirit via open-weight Gemma."""
    if payload.sector_id not in SECTOR_DATA:
        raise HTTPException(status_code=404, detail=f"Sector {payload.sector_id} not found.")

    sector = SECTOR_DATA[payload.sector_id]
    session = await get_or_create_session(payload.session_id)
    attempts = session.get("attempts", {}).get(payload.sector_id, 1)

    guidance = await get_spirit_guidance(
        spirit_name=sector["spirit_name"],
        sector_id=payload.sector_id,
        error_context=payload.error_context,
        user_query=payload.message,
        attempt_count=attempts
    )

    # Record in history logs
    await record_commune_log(payload.session_id, payload.sector_id, payload.message, guidance)

    return {
        "spirit_name": sector["spirit_name"],
        "spirit_title": sector["spirit_title"],
        "spirit_avatar": sector["spirit_avatar"],
        "guidance": guidance
    }


@app.post("/api/switch_sector")
async def switch_sector(payload: SwitchSectorRequest):
    """Switches the active sector focus for the session."""
    if payload.sector_id not in SECTOR_DATA:
        raise HTTPException(status_code=404, detail="Invalid sector ID.")
    updated = await switch_session_sector(payload.session_id, payload.sector_id)
    return updated


@app.post("/api/reset")
async def reset(payload: ResetRequest):
    """Resets memory corruption and player progress."""
    reset_data = await reset_session(payload.session_id)
    return reset_data


@app.get("/api/report/{session_id}")
async def generate_report(session_id: str):
    """Generates the downloadable System Integrity & Mastery Exorcism Report."""
    session = await get_or_create_session(session_id)
    solved = session.get("solved_sectors", [])
    integrity = session.get("integrity_score", 25)
    exorcism = integrity >= 100

    report_lines = [
        "================================================================================",
        "          AETHER-OS KERNEL DIAGNOSTIC & SYSTEM EXORCISM REPORT",
        "       Hacktoberfest 2026: Open-Source AI Challenge - Ghost in the Machine",
        "================================================================================",
        f"SESSION IDENTIFIER : {session['session_id']}",
        f"KERNEL STATUS      : {'EXORCISED // FULLY STABILIZED' if exorcism else 'CORRUPTED // UNSTABLE'}",
        f"SYSTEM INTEGRITY   : {integrity}%",
        f"CLEARED SECTORS    : {', '.join(solved) if solved else 'NONE'}",
        "--------------------------------------------------------------------------------",
        "SECTOR BREAKDOWN & ANCESTOR MASTERY:",
        ""
    ]

    for sid, sdata in SECTOR_DATA.items():
        is_cleared = sid in solved
        attempts = session.get("attempts", {}).get(sid, 0)
        status_text = "[STABILIZED]" if is_cleared else "[CORRUPTED]"
        report_lines.append(f"  * Sector {sid}: {sdata['name']} ({sdata['topic']})")
        report_lines.append(f"    Status       : {status_text}")
        report_lines.append(f"    Spirit Guide : {sdata['spirit_name']} ({sdata['spirit_title']})")
        report_lines.append(f"    Patches Sent : {attempts}")
        report_lines.append("")

    report_lines.extend([
        "--------------------------------------------------------------------------------",
        "PEDAGOGICAL & ARCHITECTURAL SUMMARY:",
        "  * Open-Weight Foundation Model : Google Gemma (gemma-2-9b-it / gemma:2b)",
        "  * Privacy & Data Sovereignty   : 100% Student Data Localized, Zero Telemetry Leaked",
        "  * Execution Sandbox Isolation : AST AST-Verified Python Subprocess (<= 2.0s)",
        "  * Socratic Policy Compliance  : Direct Code Output Strictly Prohibited",
        "================================================================================",
        "END OF TRANSMISSION // AETHER-OS DAEMON PURGE COMPLETE."
    ])

    return PlainTextResponse("\n".join(report_lines), media_type="text/plain")
