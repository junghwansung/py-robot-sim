# 시뮬레이션 엔진

## 정의

**엔진** = 시간의 흐름에 따라 시스템 상태를 갱신하는 루프와 그 루프를 구동하는 인프라 전체.

게임 엔진, 물리 엔진, 공장 시뮬레이터 모두 본질은 동일:

```
while running:
    dt = tick()          # 시간 진행
    update(world, dt)    # 상태 갱신
    render(world)        # 출력 (선택)
```

---

## 역할

| 역할 | 설명 |
|------|------|
| 시간 관리 | 실시간/배속/단계별 시간 진행 제어 |
| 상태 갱신 | 매 tick마다 모든 구성요소 상태 계산 |
| 의존성 조율 | A가 B 결과를 필요로 할 때 순서 보장 |
| 이벤트 전달 | 로봇 완료 → 컨베이어 시작 같은 인과관계 처리 |
| 시간 동기화 | 여러 요소가 같은 "지금"을 공유하도록 보장 |

---

## 구성요소

```
Engine
 ├── Clock          — 시뮬레이션 시간, dt, 배속
 ├── World          — 시뮬레이션 대상 객체들의 컨테이너
 ├── Scheduler      — 언제 무엇을 실행할지 결정
 ├── EventBus       — 객체 간 느슨한 결합 통신
 ├── SystemList     — 상태 갱신 로직 모음 (ECS의 System)
 └── Renderer       — 상태 → 시각화 (분리 가능)
```

---

## 실체: 클래스? 프로세스? 모듈?

셋 다 — 레이어가 다름.

```
프로세스 레벨:  Engine 프로세스 하나가 시뮬레이션 루프를 돌림
모듈 레벨:      engine/ 패키지 안에 clock, world, scheduler 등 모듈 분리
클래스 레벨:    Engine 클래스가 위 구성요소들을 조립하고 루프 구동
```

```python
class Engine:               # 조율자 (클래스)
    clock: Clock
    world: World
    systems: list[System]
    event_bus: EventBus

    def run(self): ...      # 루프 = 프로세스/스레드로 실행
```

---

## 추상화: ECS 패턴

공장 시뮬레이터에 가장 적합한 구조는 **Entity-Component-System**:

```
Entity    = 식별자만 있는 존재 (로봇 #1, 컨베이어 #3)
Component = 순수 데이터 (위치, 속도, 조인트값, 상태)
System    = 로직 (KinematicsSystem, ConveyorSystem, CollisionSystem)
```

```
매 tick:
  KinematicsSystem  → 모든 로봇 Entity의 joint 값으로 FK 계산
  ConveyorSystem    → 모든 컨베이어 Entity 위치 갱신
  CollisionSystem   → 충돌 감지
  EventSystem       → 이벤트 소비 및 전달
```

**ECS의 장점**: `Robot`, `Conveyor` 클래스 안에 로직을 넣으면 객체가 커지고 상호작용이 복잡해짐. ECS는 로직을 System으로 분리하여 조합 가능하게 만듦.

---

## 공장 시뮬레이터 구조 예시

```
Engine
 ├── Clock
 │    ├── sim_time: float       # 시뮬레이션 경과 시간
 │    ├── speed: float          # 1.0 = 실시간, 2.0 = 2배속
 │    └── dt: float             # 이번 tick의 시간 간격
 │
 ├── World
 │    ├── robots: list[Robot]
 │    ├── conveyors: list[Conveyor]
 │    └── sensors: list[Sensor]
 │
 ├── Systems (순서 중요)
 │    ├── TrajectorySystem      # 궤적 → joint 목표값
 │    ├── KinematicsSystem      # joint값 → FK → pose
 │    ├── ConveyorSystem        # 컨베이어 이송
 │    ├── SensorSystem          # 센서 감지
 │    └── CollisionSystem       # 충돌 감지
 │
 └── EventBus
      ├── RobotReachedTarget
      ├── PartArrived
      └── SensorTriggered
```

---

## 요약

| 질문 | 답 |
|------|-----|
| 정의 | 시간 기반 상태 갱신 루프 + 그 인프라 |
| 역할 | 시간 관리, 상태 갱신 순서 조율, 이벤트 전달 |
| 실체 | `Engine` 클래스 + `engine/` 모듈 + 루프는 프로세스/스레드 |
| 추상화 | ECS — 데이터(Component)와 로직(System) 분리 |
| 핵심 | 객체가 자신을 갱신하는 게 아니라, System이 객체를 갱신 |
