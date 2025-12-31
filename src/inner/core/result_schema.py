from __future__ import annotations
from typing import Dict, Any

"""
status:
  PASS   - 안전함
  INFO   - 정보성 결과
  WARN   - 의심되나 확정 아님
  FAIL   - 취약점 발견
  ERROR  - 스캔 자체 실패

severity:
  NONE | LOW | MEDIUM | HIGH | CRITICAL
"""

STATUS_VALUES = {"PASS", "INFO", "WARN", "FAIL", "ERROR"}
SEVERITY_VALUES = {"NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"}

REQUIRED_FIELDS = {
    "module_id",
    "target_id",
    "status",
    "severity",
    "title",
}

OPTIONAL_FIELD_TYPES = {
    "description": str,
    "recommendation": str,
    "evidence": list,
    "references": list,
    "tags": list,
    "meta": dict,
    "artifacts": dict,   
    "result_id": str,    
    "timestamp": str,    
}


class ResultSchemaError(ValueError):
    pass


def normalize_result(result: Dict[str, Any]) -> Dict[str, Any]:

    if "description" not in result:
        result["description"] = ""
    if "recommendation" not in result:
        result["recommendation"] = ""
    if "evidence" not in result:
        result["evidence"] = []
    if "references" not in result:
        result["references"] = []
    if "tags" not in result:
        result["tags"] = []
    if "meta" not in result:
        result["meta"] = {}
    if "artifacts" not in result:
        result["artifacts"] = {}
    return result


def validate_result(result: Dict[str, Any]) -> None:
    if not isinstance(result, dict):
        raise ResultSchemaError("result must be a dict")

    missing = REQUIRED_FIELDS - result.keys()
    if missing:
        raise ResultSchemaError(f"missing required fields: {', '.join(sorted(missing))}")

    status = result.get("status")
    severity = result.get("severity")

    if status not in STATUS_VALUES:
        raise ResultSchemaError(
            f"invalid status: {status} (allowed: {', '.join(sorted(STATUS_VALUES))})"
        )

    if severity not in SEVERITY_VALUES:
        raise ResultSchemaError(
            f"invalid severity: {severity} (allowed: {', '.join(sorted(SEVERITY_VALUES))})"
        )

    for k, typ in OPTIONAL_FIELD_TYPES.items():
        if k in result and result[k] is not None and not isinstance(result[k], typ):
            raise ResultSchemaError(f"{k} must be {typ.__name__}")

    if "evidence" in result:
        if not all(isinstance(x, str) for x in result["evidence"]):
            raise ResultSchemaError("evidence must be list[str]")
    if "references" in result:
        if not all(isinstance(x, str) for x in result["references"]):
            raise ResultSchemaError("references must be list[str]")
    if "tags" in result:
        if not all(isinstance(x, str) for x in result["tags"]):
            raise ResultSchemaError("tags must be list[str]")
