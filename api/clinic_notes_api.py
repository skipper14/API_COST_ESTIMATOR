# clinic_notes_api.py - one resource, every verb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AfyaPlus Clinic Notes API", version="0.1.0")

class Note(BaseModel):
    clinic: str
    text: str

# our "database" for this lesson: a dictionary in memory
NOTES: dict[int, Note] = {
    1: Note(clinic="Kisumu Central", text="Fridge repaired, vaccines restocked."),
}
NEXT_ID = 2

@app.get("/notes")
def list_notes():
    return {"count": len(NOTES), "notes": NOTES}

@app.get("/notes/{note_id}")
def get_note(note_id: int):                    # FastAPI converts the URL text to int for us
    if note_id not in NOTES:
        raise HTTPException(404, "No note with that id")
    return NOTES[note_id]

@app.post("/notes", status_code=201)           # 201 = "created", more precise than a plain 200
def create_note(note: Note):
    global NEXT_ID
    NOTES[NEXT_ID] = note
    NEXT_ID += 1
    return {"id": NEXT_ID - 1, "note": note}

@app.put("/notes/{note_id}")
def replace_note(note_id: int, note: Note):
    if note_id not in NOTES:
        raise HTTPException(404, "No note with that id")
    NOTES[note_id] = note                      # PUT replaces the whole note
    return NOTES[note_id]

class NotePatch(BaseModel):                    # every field optional: senders patch only what changed
    clinic: str | None = None
    text: str | None = None

@app.patch("/notes/{note_id}")
def update_note(note_id: int, patch: NotePatch):
    if note_id not in NOTES:
        raise HTTPException(404, "No note with that id")
    changes = patch.model_dump(exclude_unset=True)     # only the fields the caller sent
    NOTES[note_id] = NOTES[note_id].model_copy(update=changes)
    return NOTES[note_id]

@app.delete("/notes/{note_id}", status_code=204)       # 204 = "done, nothing to say back"
def delete_note(note_id: int):
    if note_id not in NOTES:
        raise HTTPException(404, "No note with that id")
    del NOTES[note_id]