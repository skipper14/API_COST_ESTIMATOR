"""TTL cache for public reference answers, never patient-specific triage."""

from dataclasses import dataclass
from time import monotonic
from typing import Callable


PUBLIC_FAQ = {
    "malaria-prevention": "Use a treated mosquito net and remove standing water.",
    "clinic-hours": "Clinic hours vary by location; confirm with the clinic.",
    "vaccine-schedule": "Confirm the current schedule with a qualified clinic.",
}


@dataclass(frozen=True)
class CacheEntry:
    answer: str
    expires_at: float


class PublicReferenceCache:
    def __init__(
        self,
        ttl_seconds: float = 300,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be greater than zero")
        self._ttl_seconds = ttl_seconds
        self._clock = clock
        self._entries: dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0

    def get(self, faq_id: str) -> str | None:
        if faq_id not in PUBLIC_FAQ:
            raise KeyError("only allow-listed public FAQ identifiers can be cached")
        entry = self._entries.get(faq_id)
        if entry is None or entry.expires_at <= self._clock():
            self._entries.pop(faq_id, None)
            self.misses += 1
            return None
        self.hits += 1
        return entry.answer

    def put(self, faq_id: str, answer: str) -> None:
        if faq_id not in PUBLIC_FAQ:
            raise KeyError("only allow-listed public FAQ identifiers can be cached")
        self._entries[faq_id] = CacheEntry(
            answer=answer,
            expires_at=self._clock() + self._ttl_seconds,
        )