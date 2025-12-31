# 📦 Inner Scanner 모듈 구조 사용설명서

이 문서는 Inner 스캐너 프레임워크에서 사용하는 플러그인 모듈 구조와 각 필드의 의미, 작성 규칙, 실행 흐름을 설명합니다.

---

## 1. 모듈 파일 개요

모든 진단 모듈은 다음 위치에 작성됩니다:
**src/inner/plugins/ <category> / <module_name>.py**

예시: src/inner/plugins/example.py

각 모듈 파일은 반드시 다음 두 요소를 포함해야 합니다.

1. MODULE 메타데이터 (dict)
2. run(ctx) 실행 함수

---

## 2. MODULE 메타데이터 구조

MODULE은 모듈의 정적 정보와 옵션 정의를 담는 딕셔너리입니다. 코어(scanner)는 이 정보를 사용해 모듈을 로딩, 선택, 검증합니다. 💦

```
MODULE = {
"id": "example/test",
"name": "Example Test Module",
"category": "example",
"description": "demo module",
"transport": [],
"targets": ["host", "url"],
"options": {...},
"references": [...],
"tags": [...],
}
```

### 2.1 주요 필드 상세

- **id (필수)**: 모듈의 고유 식별자. CLI에서 "modules use" 형태로 사용되며 중복이 금지됩니다.
- **name (필수)**: 사람이 읽는 모듈 이름. "modules list" 출력용입니다.
- **category**: 모듈 분류. 향후 배치 실행에 사용됩니다.
- **description**: 모듈의 기능 요약 설명입니다.
- **transport**: 모듈이 사용하는 전송 수단 (예: ["http"], ["ssh"], ["db"]). 코어는 이를 기반으로 ctx["clients"]를 준비합니다.
- **targets**: 모듈이 요구하는 타겟 필드 (예: "host" -> IP, "url" -> 웹 URL). targets.json에 해당 키가 없으면 실행이 불가합니다.

---

## 3. options (옵션 정의)

모듈이 사용하는 모든 옵션은 MODULE["options"]에 선언해야 합니다.

```
"options": {
    "message": {
        "type": "str",
        "required": True,
        "default": "",
        "help": "Any message to include in the result."
        }
}
```

### 옵션 필드 설명

- **type**: 값 타입 (str, int, bool)
- **required**: 필수 옵션 여부
- **default**: 기본값
- **help**: options show 시 출력되는 설명

⚠️ **중요**: required=True인데 값이 없으면 코어가 실행 전에 차단합니다.  
모듈 내부에서는 별도의 옵션 검증을 하지 않습니다.

---

## 4. run(ctx) 함수

run() 함수는 모듈의 유일한 실행 진입점입니다.

### 4.1 ctx (코어가 주입하는 실행 컨텍스트)

ctx는 딕셔너리이며, 다음 키를 가질 수 있습니다.

- **ctx["target"]**: 현재 타겟 정보
- **ctx["options"]**: 최종 옵션 (default + set 반영)
- **ctx["clients"]**: 전송 클라이언트 (http, ssh 등)
- **ctx["meta"]**: 실행 메타데이터 (선택)

### 4.2 run 함수의 책임 범위

- ✅ 진단 로직 수행 및 취약 여부 판단
- ✅ 증거(evidence) 생성 및 결과 딕셔너리 반환
- 🚫 print 사용 금지
- 🚫 파일 저장 금지
- 🚫 타겟/옵션 로딩 금지
- 🚫 상태(state) 변경 금지

---

## 5. 반환 Result 구조

run()은 반드시 다음의 표준 Result 딕셔너리를 반환해야 합니다.

```
return {
    "module_id": MODULE["id"],
    "target_id": target.get("id"),
    "status": "INFO",
    "severity": "NONE",
    "title": "...",
    "description": "...",
    "evidence": [...],
    "recommendation": "...",
    "references": [...],
    "tags": [...],
    "meta": {...}
}
```

### 주요 필드 설명

- **status**: 결과 상태 (INFO, SAFE, VULN, ERROR 등)
- **severity**: 심각도 (NONE, LOW, MEDIUM, HIGH, CRITICAL)
- **evidence**: 판단 근거
- **recommendation**: 대응 방안

---

## 6. 실행 흐름 요약

1. Core가 MODULE 로드
2. 옵션 default + set 병합
3. ctx 구성
4. **run(ctx) 호출 (모듈의 책임)**
5. Result 수집
6. 출력 / 리포트 / 저장

---

## 7. 모듈 작성 핵심 원칙

- ✔️ **모듈은 판단만 한다**
- ✔️ **준비·실행·저장은 코어의 책임**
- ✔️ **ctx와 Result는 계약(contract) 이다**
