import os
import json
import sqlite3
from typing import List, Optional
from ..models.incident_event import IncidentEvent

class TimelineRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS timeline_events (
                    incident_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    sha256_hash TEXT NOT NULL
                )
            """)
            conn.commit()

    def add_event(self, event: IncidentEvent) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO timeline_events 
                    (incident_id, timestamp, event_type, severity, description, metadata, sha256_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.incident_id,
                    event.timestamp,
                    event.event_type,
                    event.severity,
                    event.description,
                    json.dumps(event.metadata),
                    event.sha256_hash
                ))
                conn.commit()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to insert timeline event: {e}")
            return False

    def get_events(self, filter_type: Optional[str] = None, limit: int = 500) -> List[IncidentEvent]:
        events = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if filter_type:
                    cursor.execute("""
                        SELECT incident_id, timestamp, event_type, severity, description, metadata, sha256_hash
                        FROM timeline_events
                        WHERE event_type = ?
                        ORDER BY timestamp DESC LIMIT ?
                    """, (filter_type, limit))
                else:
                    cursor.execute("""
                        SELECT incident_id, timestamp, event_type, severity, description, metadata, sha256_hash
                        FROM timeline_events
                        ORDER BY timestamp DESC LIMIT ?
                    """, (limit,))
                
                rows = cursor.fetchall()
                for r in rows:
                    events.append(IncidentEvent(
                        incident_id=r[0],
                        timestamp=r[1],
                        event_type=r[2],
                        severity=r[3],
                        description=r[4],
                        metadata=json.loads(r[5]) if r[5] else {},
                        sha256_hash=r[6]
                    ))
        except Exception as e:
            print(f"[ERROR] Failed to fetch timeline events: {e}")
        return events

    def close(self):
        pass

