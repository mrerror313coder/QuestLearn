"""Database persistence layer for QuestLearn: Shadows of the Machine.

Provides asynchronous MongoDB Atlas integration via motor with an automatic
zero-dependency fallback to local SQLite (questlearn.db) via aiosqlite.
"""
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.config import settings

# Global state handles
_mongo_client = None
_mongo_db = None
_use_sqlite = True
SQLITE_DB_PATH = "questlearn.db"


async def init_db():
    """Initializes MongoDB Atlas connection or sets up the local SQLite database."""
    global _mongo_client, _mongo_db, _use_sqlite

    if settings.MONGO_URI and settings.MONGO_URI.startswith("mongodb"):
        try:
            # Ensure reliable DNS resolution for MongoDB Atlas SRV records
            try:
                import dns.resolver
                resolver = dns.resolver.Resolver()
                resolver.nameservers = ['8.8.8.8', '1.1.1.1']
                dns.resolver.default_resolver = resolver
            except Exception:
                pass

            from motor.motor_asyncio import AsyncIOMotorClient
            _mongo_client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
            # Ping database to verify connection
            await _mongo_client.admin.command('ping')
            _mongo_db = _mongo_client.get_database("questlearn")
            _use_sqlite = False
            print("[DATABASE]: Connected to MongoDB Atlas successfully! Persistence active in cloud.")
            return
        except Exception as exc:
            print(f"[DATABASE]: MongoDB connection failed ({type(exc).__name__}: {exc}). Falling back to local SQLite.")
            _use_sqlite = True

    # Fallback to SQLite
    _use_sqlite = True
    import aiosqlite
    async with aiosqlite.connect(SQLITE_DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                current_sector TEXT,
                integrity_score INTEGER,
                solved_sectors TEXT,
                attempts TEXT,
                history_logs TEXT,
                created_at REAL,
                updated_at REAL
            )
        """)
        await db.commit()


def _calculate_integrity(solved_sectors: List[str]) -> int:
    """Calculate system integrity based on solved sectors:
    Base integrity: 25% (unstable)
    Each sector adds 25%. All 3 solved = 100% (Exorcism achieved!)
    """
    count = len(set(solved_sectors))
    if count >= 3:
        return 100
    return 25 + (count * 25)


async def get_or_create_session(session_id: str) -> Dict[str, Any]:
    """Retrieves an existing session or initializes a new player session."""
    now = time.time()
    default_session = {
        "session_id": session_id,
        "current_sector": "0x01",
        "integrity_score": 25,
        "solved_sectors": [],
        "attempts": {"0x01": 0, "0x02": 0, "0x03": 0},
        "history_logs": [
            {
                "timestamp": now,
                "event": "BOOT_SEQUENCE",
                "message": "AetherOS terminal initialized. Memory Corruption: 75%."
            }
        ],
        "created_at": now,
        "updated_at": now
    }

    if not _use_sqlite and _mongo_db is not None:
        doc = await _mongo_db.sessions.find_one({"session_id": session_id})
        if doc:
            doc.pop("_id", None)
            return doc
        await _mongo_db.sessions.insert_one(default_session)
        return default_session

    # SQLite
    import aiosqlite
    async with aiosqlite.connect(SQLITE_DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "session_id": row["session_id"],
                    "current_sector": row["current_sector"],
                    "integrity_score": row["integrity_score"],
                    "solved_sectors": json.loads(row["solved_sectors"]),
                    "attempts": json.loads(row["attempts"]),
                    "history_logs": json.loads(row["history_logs"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }

        # Create new
        await db.execute(
            """INSERT INTO sessions 
               (session_id, current_sector, integrity_score, solved_sectors, attempts, history_logs, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id,
                default_session["current_sector"],
                default_session["integrity_score"],
                json.dumps(default_session["solved_sectors"]),
                json.dumps(default_session["attempts"]),
                json.dumps(default_session["history_logs"]),
                default_session["created_at"],
                default_session["updated_at"]
            )
        )
        await db.commit()
        return default_session


async def update_session_patch(
    session_id: str,
    sector_id: str,
    passed: bool,
    code: str,
    error_msg: str = ""
) -> Dict[str, Any]:
    """Updates session state after a patch submission."""
    session = await get_or_create_session(session_id)
    now = time.time()

    attempts = session.get("attempts", {})
    attempts[sector_id] = attempts.get(sector_id, 0) + 1

    solved_sectors = set(session.get("solved_sectors", []))
    if passed:
        solved_sectors.add(sector_id)
        # Advance to next sector if available
        next_sector = "0x02" if sector_id == "0x01" else ("0x03" if sector_id == "0x02" else sector_id)
    else:
        next_sector = session.get("current_sector", sector_id)

    solved_list = sorted(list(solved_sectors))
    new_integrity = _calculate_integrity(solved_list)

    log_entry = {
        "timestamp": now,
        "event": "PATCH_SUBMISSION",
        "sector_id": sector_id,
        "passed": passed,
        "error_msg": error_msg[:200] if error_msg else ""
    }
    history = session.get("history_logs", [])
    history.append(log_entry)

    updated_data = {
        "session_id": session_id,
        "current_sector": next_sector,
        "integrity_score": new_integrity,
        "solved_sectors": solved_list,
        "attempts": attempts,
        "history_logs": history,
        "created_at": session.get("created_at", now),
        "updated_at": now
    }

    if not _use_sqlite and _mongo_db is not None:
        await _mongo_db.sessions.update_one(
            {"session_id": session_id},
            {"$set": updated_data}
        )
        return updated_data

    # SQLite
    import aiosqlite
    async with aiosqlite.connect(SQLITE_DB_PATH) as db:
        await db.execute(
            """UPDATE sessions SET
               current_sector = ?,
               integrity_score = ?,
               solved_sectors = ?,
               attempts = ?,
               history_logs = ?,
               updated_at = ?
               WHERE session_id = ?""",
            (
                next_sector,
                new_integrity,
                json.dumps(solved_list),
                json.dumps(attempts),
                json.dumps(history),
                now,
                session_id
            )
        )
        await db.commit()
    return updated_data


async def record_commune_log(session_id: str, sector_id: str, query: str, response: str) -> None:
    """Logs a Socratic commune exchange into session history."""
    session = await get_or_create_session(session_id)
    now = time.time()
    history = session.get("history_logs", [])
    history.append({
        "timestamp": now,
        "event": "COMMUNE_DIALOGUE",
        "sector_id": sector_id,
        "query": query[:200],
        "response_preview": response[:200]
    })

    if not _use_sqlite and _mongo_db is not None:
        await _mongo_db.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"history_logs": history, "updated_at": now}}
        )
        return

    import aiosqlite
    async with aiosqlite.connect(SQLITE_DB_PATH) as db:
        await db.execute(
            "UPDATE sessions SET history_logs = ?, updated_at = ? WHERE session_id = ?",
            (json.dumps(history), now, session_id)
        )
        await db.commit()


async def switch_session_sector(session_id: str, sector_id: str) -> Dict[str, Any]:
    """Allows user to manually change active sector focus."""
    session = await get_or_create_session(session_id)
    now = time.time()
    session["current_sector"] = sector_id
    session["updated_at"] = now

    if not _use_sqlite and _mongo_db is not None:
        await _mongo_db.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"current_sector": sector_id, "updated_at": now}}
        )
        return session

    import aiosqlite
    async with aiosqlite.connect(SQLITE_DB_PATH) as db:
        await db.execute(
            "UPDATE sessions SET current_sector = ?, updated_at = ? WHERE session_id = ?",
            (sector_id, now, session_id)
        )
        await db.commit()
    return session


async def reset_session(session_id: str) -> Dict[str, Any]:
    """Resets memory corruption and player progress for a fresh quest."""
    now = time.time()
    reset_data = {
        "session_id": session_id,
        "current_sector": "0x01",
        "integrity_score": 25,
        "solved_sectors": [],
        "attempts": {"0x01": 0, "0x02": 0, "0x03": 0},
        "history_logs": [
            {
                "timestamp": now,
                "event": "SYSTEM_PURGE",
                "message": "Memory registers reset to unpatched state."
            }
        ],
        "created_at": now,
        "updated_at": now
    }

    if not _use_sqlite and _mongo_db is not None:
        await _mongo_db.sessions.update_one(
            {"session_id": session_id},
            {"$set": reset_data},
            upsert=True
        )
        return reset_data

    import aiosqlite
    async with aiosqlite.connect(SQLITE_DB_PATH) as db:
        await db.execute(
            """UPDATE sessions SET
               current_sector = ?,
               integrity_score = ?,
               solved_sectors = ?,
               attempts = ?,
               history_logs = ?,
               updated_at = ?
               WHERE session_id = ?""",
            (
                "0x01",
                25,
                json.dumps([]),
                json.dumps({"0x01": 0, "0x02": 0, "0x03": 0}),
                json.dumps(reset_data["history_logs"]),
                now,
                session_id
            )
        )
        await db.commit()
    return reset_data
