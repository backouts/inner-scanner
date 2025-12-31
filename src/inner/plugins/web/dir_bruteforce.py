from __future__ import annotations
from typing import Any, Dict, List
from urllib.parse import urljoin
import os

import requests

MODULE = {
    "id": "web/dir_bruteforce",
    "name": "Web Directory Bruteforce",
    "category": "web",
    "description": "Discover common directories/files by trying wordlist paths.",
    "transport": ["http"],
    "targets": ["url", "host"],

    "options": {
        "base_url": {
            "type": "str",
            "required": False,
            "default": "",
            "help": "기본 URL. 비우면 target.url 또는 http://target.host 를 사용"
        },
        "wordlist": {
            "type": "str",
            "required": True,
            "default": "data/wordlists/common.txt",
            "help": "브루트포싱할 경로 워드리스트 파일"
        },
        "timeout": {
            "type": "int",
            "required": False,
            "default": 5,
            "help": "HTTP timeout seconds"
        },
        "status_allow": {
            "type": "list[str]",
            "required": False,
            "default": ["200", "204", "301", "302", "307", "308", "401", "403"],
            "help": "발견으로 취급할 HTTP 상태코드 목록 (문자열 리스트)"
        },
        "max_hits": {
            "type": "int",
            "required": False,
            "default": 50,
            "help": "최대 발견 개수(너무 많아지는 것 방지)"
        },
        "dry_run": {
            "type": "bool",
            "required": False,
            "default": False,
            "help": "true면 실제 요청 없이 시뮬레이션"
        },
    },

    "references": ["KISA-WEB-DIR-BRUTE-0001"],
    "tags": ["web", "discovery", "bruteforce"],
}


def _infer_base_url(target: Dict[str, Any], opt_base: str) -> str:
    if opt_base and opt_base.strip():
        return opt_base.strip()

    if target.get("url"):
        u = str(target["url"]).strip()
        if u.startswith("http://") or u.startswith("https://"):
            return u
        return "http://" + u

    host = target.get("host")
    if host:
        return f"http://{host}"

    return ""


def _read_wordlist(path: str) -> List[str]:
    if not os.path.exists(path):
        raise ValueError(f"wordlist not found: {path}")

    words: List[str] = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if not s.startswith("/"):
                s = "/" + s
            words.append(s)
    return words


def run(ctx: Dict[str, Any]) -> Dict[str, Any]:
    target = (ctx.get("target") or {})
    options = (ctx.get("options") or {})

    base_url = _infer_base_url(target, options.get("base_url", ""))
    if not base_url:
        return {
            "module_id": MODULE["id"],
            "target_id": target.get("id"),
            "status": "ERROR",
            "severity": "NONE",
            "title": "Base URL not available",
            "description": "target.url 또는 target.host가 없어 base_url을 만들 수 없습니다.",
            "evidence": [f"target={target}"],
            "recommendation": "targets set <id> url=... 또는 host=... 로 설정하세요.",
            "references": MODULE.get("references", []),
            "tags": MODULE.get("tags", []),
            "meta": {"base_url": None},
            # artifacts는 없음
        }

    wordlist_path = str(options.get("wordlist") or "").strip()
    timeout = int(options.get("timeout", 5))
    allow = options.get("status_allow") or []
    allow_set = {str(x).strip() for x in allow}
    max_hits = int(options.get("max_hits", 50))
    dry_run = bool(options.get("dry_run", False))

    words = _read_wordlist(wordlist_path)

    hits: List[str] = []
    evidence: List[str] = [
        f"base_url={base_url}",
        f"wordlist={wordlist_path}",
        f"timeout={timeout}",
        f"allow={sorted(list(allow_set))}",
        f"max_hits={max_hits}",
        f"dry_run={dry_run}",
    ]

    for path in words:
        if len(hits) >= max_hits:
            break

        full = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))

        if dry_run:
            continue

        try:
            r = requests.get(full, timeout=timeout, allow_redirects=False)
            code = str(r.status_code)
            if code in allow_set:
                hits.append(full)
                evidence.append(f"HIT {code} {full}")
        except requests.RequestException as e:
            evidence.append(f"ERR {full} {type(e).__name__}")

    status = "PASS"
    severity = "NONE"
    title = "No interesting paths found"
    desc = "리스트 기반으로 디렉터리/파일 스캔을 시도했으나 유의미한 응답을 찾지 못했습니다."

    if dry_run:
        status = "INFO"
        title = "Dry-run completed"
        desc = "dry_run=true 이므로 실제 요청 없이 종료했습니다."

    if hits:
        status = "INFO"
        title = f"Found {len(hits)} candidate paths"
        desc = "디렉터리/파일 후보를 발견했습니다. 후속 모듈(백업파일/설정노출/디렉터리리스팅 등)에서 재검증하세요."

    result: Dict[str, Any] = {
        "module_id": MODULE["id"],
        "target_id": target.get("id"),

        "status": status,
        "severity": severity,

        "title": title,
        "description": desc,
        "evidence": evidence,
        "recommendation": "발견된 경로에 대해 민감정보 노출/설정파일/백업파일/권한오류 등을 후속 점검하세요.",

        "references": MODULE.get("references", []),
        "tags": MODULE.get("tags", []),
        "meta": {
            "base_url": base_url,
            "hits": len(hits),
        },
    }

    if hits:
        result["artifacts"] = {
            "web": {
                "urls": hits
            }
        }

    return result
