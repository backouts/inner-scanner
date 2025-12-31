# Inner Scanner 모듈 작성 가이드 (한글)

이 문서는 모듈을 만드는 사람이 프레임워크 내부 구현을 몰라도  
모듈을 추가할 수 있도록 만든 규격서입니다.

---

## 0. 모듈이란?

모듈은 `run(ctx)` 함수 하나로 실행되는 "진단 로직 단위"입니다.

- 입력: ctx (타겟/옵션/이전 아티팩트/클라이언트)
- 출력: result dict (리포트/저장에 그대로 사용)

---

## 1. 모듈 파일 위치

모듈은 아래 폴더 아래에 Python 파일로 둡니다.

- 위치: `src/inner/plugins/<category>/<module_name>.py`

예)

- `src/inner/plugins/web/dir_bruteforce.py`

※ registry(load_modules)가 이 경로를 스캔해 모듈을 불러옵니다.

---

## 2. MODULE 메타데이터 (필수)

모든 모듈은 전역 변수 `MODULE` dict를 반드시 가져야 합니다.

필수 키:

- id: 모듈 ID (예: "web/dir_bruteforce")
- name: 표시 이름
- category: 분류 (예: "web")
- description: 한 줄 설명
- targets: 이 모듈이 처리 가능한 타겟 타입 목록 (예: ["url"], ["host"] ["host","url"])
- options: 옵션 스펙 dict
- tags: 검색/분류 태그 (list)

예시:

```python
MODULE = {
  "id": "web/dir_bruteforce",
  "name": "Web Directory Bruteforce",
  "category": "web",
  "description": "Common directory discovery",
  "targets": ["url"],
  "options": {
    "wordlist": {
      "type": "str",
      "required": True,
      "default": "common.txt",
      "help": "워드리스트 파일 경로"
    },
    "timeout": {
      "type": "int",
      "required": False,
      "default": 5,
      "help": "요청 타임아웃(초)"
    }
  },
  "tags": ["web", "discovery"]
}
```

## 3. run(ctx) (필수) 💦

모든 모듈은 아래 시그니처를 반드시 구현해야 합니다.

** signature: def run(ctx: dict) -> dict **

### 📥 ctx 객체 구성 요소

- ctx["target"] : 현재 선택된 타겟(dict)
- ctx["options"]: 모듈 옵션(dict) (default + set 반영)
- ctx["artifacts"]: 이전 실행 결과에서 누적된 아티팩트(dict) (선택)
- ctx["clients"]: 프로토콜 클라이언트(dict) (예: {"http": ..., "ssh": ...}) (선택)
- ctx["meta"]: 실행 메타데이터(dict) (선택)

---

## 4. Result 반환 규격 (필수) 💕

run()은 result dict를 반환해야 하며, 최소 필드는 아래와 같습니다:

- module_id (str): 모듈 고유 식별자
- target_id (str or None): 타겟 식별자
- status (str): PASS / INFO / WARN / FAIL / ERROR
- severity (str): NONE / LOW / MEDIUM / HIGH / CRITICAL
- title (str): 결과 요약 제목
- description (str): 상세 설명
- evidence (list[str]): 증거 자료 리스트
- recommendation (str): 조치 권고 사항
- references (list[str]): 참고 링크
- tags (list[str]): 태그
- meta (dict): 실행 메타데이터

** 권장(선택): artifacts (dict) - 다음 모듈에서 재사용할 데이터 **

---

## 5. 아티팩트(artifacts) 규칙 (권장) 😈

아티팩트는 "발견한 데이터"를 다음 모듈로 넘기기 위한 구조입니다.

### 📂 권장 네임스페이스

- artifacts.web.urls : 발견한 URL/경로 목록.
- artifacts.web.params : 발견한 파라미터 목록.
- artifacts.ssh.users : 발견한 사용자 목록

** 예시 구조 **
{
"artifacts": {
"web": {
"urls": ["/admin", "/backup"]
}
}
}

---

## 6. 모듈 개발 체크리스트 💦

- [ ] MODULE["id"]가 고유한가?
- [ ] options type/required/default/help를 채웠는가?
- [ ] run(ctx)에서 target/options를 꺼내 사용했는가?
- [ ] result schema 필드를 빠짐없이 반환했는가?
- [ ] 발견 데이터가 있으면 artifacts로 반환했는가?
