import json
from pathlib import Path

class TargetStore:
    def __init__(self, path: str = "data/targets.json"):
        self.path = Path(path)

    def _load(self) -> dict:
        if not self.path.exists():
            return {"schema_version": 1, "targets": []}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if "targets" not in data:
            data["targets"] = []
        if "schema_version" not in data:
            data["schema_version"] = 1
        return data

    def _save(self, data: dict) -> None:
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def list(self) -> list[dict]:
        return self._load().get("targets", [])

    def get(self, target_id: str) -> dict | None:
        for t in self.list():
            if t.get("id") == target_id:
                return t
        return None

    def add(self, target: dict) -> None:
        if not target.get("id"):
            raise ValueError("target.id is required")

        data = self._load()
        targets = data.get("targets", [])

        if any(t.get("id") == target["id"] for t in targets):
            raise ValueError(f"target id already exists: {target['id']}")

        targets.append(target)
        data["targets"] = targets
        self._save(data)

    def update(self, target_id: str, new_target: dict) -> None:
        if not target_id:
            raise ValueError("target_id is required")
        if not new_target or new_target.get("id") != target_id:
            raise ValueError("new_target.id must match target_id")

        data = self._load()
        targets = data.get("targets", [])

        for i, t in enumerate(targets):
            if t.get("id") == target_id:
                targets[i] = new_target
                data["targets"] = targets
                self._save(data)
                return

        raise ValueError(f"target not found: {target_id}")

    def remove(self, target_id: str) -> None:
        if not target_id:
            raise ValueError("target_id is required")

        data = self._load()
        targets = data.get("targets", [])

        new_targets = [t for t in targets if t.get("id") != target_id]
        if len(new_targets) == len(targets):
            raise ValueError(f"target not found: {target_id}")

        data["targets"] = new_targets
        self._save(data)
