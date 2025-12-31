from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Iterable, Optional
from inner.core.result_schema import validate_result, ResultSchemaError
import json
import uuid

class ResultStore:
    def __init__(self, path: str = "data/results.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _assign_result_id(self, result: dict) -> dict:
        if "result_id" not in result or not result["result_id"]:
            result["result_id"] = uuid.uuid4().hex[:12]
        return result

    def append(self, result: Dict[str, Any]) -> None:
        try:
            validate_result(result)
        except ResultSchemaError:
            raise
        
        result = self._assign_result_id(result)
        line = json.dumps(result, ensure_ascii=False)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def iter_all(self) -> Iterable[Dict[str, Any]]:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

    def list(
        self,
        *,
        target_id: Optional[str] = None,
        module_id: Optional[str] = None,
        status: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> list[Dict[str, Any]]:
        out = []
        for r in self.iter_all():
            if target_id and r.get("target_id") != target_id:
                continue
            if module_id and r.get("module_id") != module_id:
                continue
            if status and r.get("status") != status:
                continue
            if severity and r.get("severity") != severity:
                continue
            out.append(r)
        return out

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()
    
    def remove_by_id(self, result_id: str) -> int:
        if not self.path.exists():
            return 0

        kept = []
        removed = 0

        for r in self.iter_all() or []:
            if r.get("result_id") == result_id:
                removed += 1
            else:
                kept.append(r)

        if removed == 0:
            return 0

        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            for r in kept:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        tmp.replace(self.path)
        return removed
    
    def aggregate_artifacts(
            self,
            target_id: str,
            *,
            module_id: Optional[str] = None,
        ) -> Dict[str, Any]:

        if not target_id:
            raise ValueError("target_id is required")

        merged: Dict[str, Any] = {}

        for r in self.iter_all() or []:
            if r.get("target_id") != target_id:
                continue
            if module_id and r.get("module_id") != module_id:
                continue

            a = r.get("artifacts")
            if not a or not isinstance(a, dict):
                continue

            self._deep_merge(merged, a)

        return merged

    def _deep_merge(self, base: Dict[str, Any], inc: Dict[str, Any]) -> None:
        for k, v in inc.items():
            if v is None:
                continue

            if isinstance(v, dict):
                cur = base.get(k)
                if not isinstance(cur, dict):
                    base[k] = {}
                self._deep_merge(base[k], v)

            elif isinstance(v, list):
                cur = base.get(k)
                if not isinstance(cur, list):
                    base[k] = []
                    cur = base[k]
                for item in v:
                    if item not in cur:
                        cur.append(item)

            else:
                base[k] = v
