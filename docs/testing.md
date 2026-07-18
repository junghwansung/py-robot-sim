# 테스트 방식

## self-check (`if __name__ == "__main__"`)

각 모듈 하단에 `assert` 기반 self-check 블록을 작성한다.

```python
if __name__ == "__main__":
    r = Range(0.0, 10.0)
    assert r.clamp(-1.0) == 0.0
    assert r.clamp(11.0) == 10.0
    print("Range: all assertions passed")
```

### 실행

```bash
uv run python packages/zmath/src/zmath/range.py
```

### 언제 작성하나

- 비자명한 로직 (분기, 루프, 수식) 포함 시
- 단순 getter/setter 같은 trivial 코드는 생략

### 한계

- 개발자가 **수동으로** 실행해야 함
- CI에서 자동 수집 안 됨 (pytest가 인식 불가)
- 통합 테스트 불가

## pytest (추후)

자동화가 필요해지면 `tests/` 디렉토리에 `test_*.py` 추가.
현재는 self-check으로 충분.
