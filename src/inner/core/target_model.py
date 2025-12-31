from __future__ import annotations
from inner.core.target_schema import new_target

class TargetModel:

    def __init__(self):
        self.schema = new_target()

    # --- public ---
    def normalize(self, raw: dict) -> dict:
        if raw is None:
            return None
        t = self._merge_with_schema(raw)
        self._infer_type(t)
        self._clean_strings(t)
        self._validate(t)
        return t

    def apply_update(self, current: dict, patch: dict, unset_paths: list[str]) -> dict:
        base = self._merge_with_schema(current)

        # 스키마 외 차단
        self._assert_patch_allowed(patch)

        # patch 적용
        merged = self._deep_merge(base, patch)

        # unset 적용
        for p in unset_paths:
            self._assert_path_allowed(p)
            self._unset_path(merged, p)

        self._infer_type(merged)
        self._clean_strings(merged)
        self._validate(merged)
        return merged

    # --- internal ---
    def _merge_with_schema(self, raw: dict) -> dict:
        base = new_target()
        for k, v in (raw or {}).items():
            if k in ("auth", "meta") and isinstance(v, dict) and isinstance(base.get(k), dict):
                base[k].update(v)
            else:
                base[k] = v
        return base

    def _infer_type(self, t: dict) -> None:
        t["type"] = "url" if t.get("url") else "host"

    def _clean_strings(self, t: dict) -> None:
        if isinstance(t.get("host"), str) and not t["host"].strip():
            t["host"] = None
        if isinstance(t.get("url"), str) and not t["url"].strip():
            t["url"] = None

    def _validate(self, t: dict) -> None:
        if not t.get("id"):
            raise ValueError("id is required")
        if not t.get("host") and not t.get("url"):
            raise ValueError("either host or url must be provided")
        if t.get("type") not in ("host", "url"):
            raise ValueError("internal error: invalid inferred type")

        ssh = (t.get("auth") or {}).get("ssh")
        if ssh is not None:
            if not isinstance(ssh, dict):
                raise ValueError("auth.ssh must be an object")
            if not ssh.get("host"):
                raise ValueError("auth.ssh.host is required when ssh auth is set")
            port = ssh.get("port")
            if port is not None and not isinstance(port, int):
                raise ValueError("auth.ssh.port must be int")

    # ---- schema allowlist checks ----
    def _assert_patch_allowed(self, patch: dict) -> None:
        for path in self._leaf_paths(patch):
            self._assert_path_allowed(path)

    def _assert_path_allowed(self, path: str) -> None:
        cur = self.schema
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur:
                raise ValueError(f"unknown field: {path}")
            cur = cur[part]

    def _leaf_paths(self, d: dict, prefix: str = "") -> list[str]:
        out = []
        for k, v in (d or {}).items():
            p = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                out.extend(self._leaf_paths(v, p))
            else:
                out.append(p)
        return out

    def _deep_merge(self, a: dict, b: dict) -> dict:
        out = dict(a)
        for k, v in (b or {}).items():
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k] = self._deep_merge(out[k], v)
            else:
                out[k] = v
        return out

    def _unset_path(self, d: dict, path: str) -> None:
        keys = path.split(".")
        cur = d
        for k in keys[:-1]:
            if k not in cur or not isinstance(cur[k], dict):
                return
            cur = cur[k]
        cur.pop(keys[-1], None)
