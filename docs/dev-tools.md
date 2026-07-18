# Dev Tools 설정

## 설치된 도구

| 도구 | 역할 |
|------|------|
| `black` | 코드 포맷터 |
| `isort` | import 정렬 |
| `pylint` | 정적 분석 / 린터 |
| `mypy` | 정적 타입 체커 |

모두 `pyproject.toml`의 `[dependency-groups] dev`에 정의됨.

## 설치

```bash
uv sync --all-packages
```

## 사용법

```bash
# 포맷
uv run black packages/

# import 정렬
uv run isort packages/

# 린트
uv run pylint packages/

# 타입 체크
uv run mypy packages/
```

## 설정 (pyproject.toml)

### black
- `line-length = 100` (기본값)
- `target-version = ["py311"]`

### isort
- `profile = "black"` — black과 충돌 없이 호환
- `line_length = 100`

### mypy
- `strict = true` — 엄격한 타입 체크
- `ignore_missing_imports = true` — 타입 스텁 없는 외부 패키지 무시

### pylint
- `max-line-length = 100` — black과 일치
- docstring 관련 경고 비활성화 (`missing-*-docstring`)

## workspace 참고

`packages/zmath` 등 workspace member 의존성 설치 시:

```bash
uv sync --all-packages   # 전체 workspace 동기화
uv add --dev <패키지>     # dev 의존성 추가
```
