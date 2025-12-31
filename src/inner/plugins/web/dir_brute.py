"""
MODULE web dir brute forcing
"""

MODULE = {
    "id": "category/name",
    "name": "Module Name",
    "category": "category",
    "description": "",
    "targets": ["host", "url"],
    "options": {},
    "tags": [],
}

def run(ctx):
    target = ctx.get("target")
    options = ctx.get("options")
    artifacts = ctx.get("artifacts", {})

    return {
        "module_id": MODULE["id"],
        "target_id": target.get("id") if target else None,
        "status": "INFO",
        "severity": "NONE",
        "title": "",
        "description": "",
        "evidence": [],
        "recommendation": "",
        "references": [],
        "tags": MODULE.get("tags", []),
        "meta": {},
        # "artifacts": {}
    }