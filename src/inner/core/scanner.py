from __future__ import annotations
from inner.core.storage.target_store import TargetStore
from inner.core.target_model import TargetModel
from inner.plugins.registry import load_modules

class Scanner:
    def __init__(self):
        self.store = TargetStore()
        self.model = TargetModel()
        self.modules = load_modules()

    def add_target(self, raw: dict):
        t = self.model.normalize(raw)
        self.store.add(t)

    def get_target(self, tid: str):
        t = self.store.get(tid)
        return self.model.normalize(t) if t else None

    def list_targets(self):
        return [self.model.normalize(t) for t in self.store.list()]

    def update_target(self, tid: str, patch: dict):
        cur = self.store.get(tid)
        if not cur:
            raise ValueError(f"target not found: {tid}")

        unset = patch.pop("__unset__", [])
        updated = self.model.apply_update(cur, patch, unset)
        self.store.update(tid, updated)

    def remove_target(self, tid: str):
        self.store.remove(tid)

    def get_module(self, mid: str):
        return self.modules.get(mid)