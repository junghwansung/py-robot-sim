# 공장 시뮬레이션 엔진의 개념과 설계

## 1. 엔진의 정의

공장 시뮬레이션 엔진은 공장의 상태를 보유하고, 시간의 흐름에 따라 정해진 규칙을 실행하여 다음 상태를 계산하는 핵심 실행 시스템이다.

이를 개념적으로 표현하면 다음과 같다.

```text
다음 상태 = 현재 상태 + 입력 + 경과 시간 + 시뮬레이션 규칙
```

또는 함수 형태로 볼 수 있다.

```python
next_world = simulate(
    current_world,
    commands,
    elapsed_time,
)
```

엔진은 단순한 데이터 저장소나 화면을 그리는 UI가 아니다. 엔진은 시뮬레이션 시간과 실행 순서를 통제하면서 공장 구성요소의 상태를 실제로 변화시키는 실행 주체다.

핵심 책임은 다음과 같다.

- 현재 공장 상태를 관리한다.
- 시뮬레이션 시간을 진행한다.
- 로봇, 컨베이어, 센서, 설비 등의 동작 규칙을 실행한다.
- 구성요소 사이의 상호작용을 처리한다.
- 외부 명령과 예약된 이벤트를 처리한다.
- 계산 결과와 발생한 이벤트를 외부에 제공한다.
- 실행 순서와 결과의 재현 가능성을 보장한다.

## 2. 엔진의 실체

엔진이 클래스인지, 모듈인지, 프로세스인지는 서로 배타적인 질문이 아니다. 각각 엔진을 바라보는 관점이 다르다.

| 관점 | 엔진의 모습 |
|---|---|
| 개념 | 시뮬레이션을 진행하는 핵심 서브시스템 |
| 코드 구조 | 여러 모듈과 클래스의 집합 |
| 외부 API | `step()`, `run()`, `pause()`, `reset()` 등을 제공하는 객체 |
| 실행 구조 | 하나 이상의 프로세스나 스레드 위에서 동작하는 런타임 |
| 배포 구조 | 라이브러리, 서버 또는 독립 실행 프로그램 |

외부에서는 하나의 엔진 객체처럼 사용할 수 있다.

```python
engine = SimulationEngine(world, systems)

engine.initialize()
engine.start()
engine.step(0.01)
engine.pause()
engine.reset()
```

하지만 내부적으로는 여러 책임이 분리된 서브시스템으로 구성된다.

```text
SimulationEngine
├── SimulationClock
├── World
├── CommandQueue
├── EventQueue
├── Scheduler
├── RobotSystem
├── ConveyorSystem
├── CollisionSystem
└── SensorSystem
```

`SimulationEngine`은 엔진의 진입점을 제공하는 파사드가 될 수 있지만, 하나의 클래스가 모든 로직을 직접 담당해서는 안 된다.

## 3. 핵심 모델: World, Component, System

### 3.1 World

`World`는 현재 공장 전체의 상태와 구성요소 집합을 나타낸다.

```text
World
├── Robots
├── Conveyors
├── Sensors
├── Products
├── Machines
├── Fixtures
└── Environment
```

World가 답해야 하는 핵심 질문은 "공장에 무엇이 존재하며 현재 어떤 상태인가?"이다.

```python
class World:
    def __init__(self):
        self.components: dict[ComponentId, Component] = {}
```

### 3.2 Component

`Component`는 공장을 구성하는 개별 요소다.

예시는 다음과 같다.

- Robot
- Conveyor
- Machine
- Sensor
- Product
- Gripper
- PLC
- SafetyFence

Component는 일반적으로 정체성과 상태를 가진다.

```python
class Component:
    id: ComponentId
    name: str
    transform: Transform
    enabled: bool
```

모든 Component가 자체 `update()` 메서드로 다른 객체를 직접 갱신하게 만들 필요는 없다. 각 객체가 임의로 다른 객체를 변경하면 의존 관계와 실행 순서를 통제하기 어려워진다.

### 3.3 System

`System`은 특정한 시뮬레이션 규칙을 실행하고 World의 상태를 변경한다.

```python
class RobotSystem:
    def update(self, world: World, dt: float) -> None:
        ...
```

대표적인 System은 다음과 같다.

- `MotionSystem`: 위치, 속도 및 이동 상태 계산
- `RobotSystem`: 로봇 명령과 궤적 실행
- `ConveyorSystem`: 컨베이어와 제품 이동 처리
- `CollisionSystem`: 충돌 검사와 대응
- `SensorSystem`: 센서 상태 계산
- `ProcessSystem`: 가공, 조립 및 대기 시간 처리
- `ControlSystem`: PLC 또는 외부 제어기와 연동

세 개념의 역할은 다음과 같이 요약할 수 있다.

```text
Component = 상태와 정체성
System    = 상태를 변경하는 규칙
Engine    = System들을 정해진 순서로 실행하는 런타임
```

다만 `Kinematics`처럼 특정 도메인 객체에 강하게 속한 계산 기능까지 모두 System으로 분리할 필요는 없다. System은 여러 객체의 상태를 일괄 처리하거나 상호작용과 실행 순서를 통제해야 할 때 특히 유용하다.

## 4. 시뮬레이션 시간

시뮬레이션 시간은 현실의 벽시계 시간과 분리해야 한다.

```python
simulation_time += dt
```

이렇게 분리하면 다음 실행 방식을 지원할 수 있다.

- 실시간 실행
- 일시정지와 재개
- 단일 스텝 실행
- 배속 또는 저속 실행
- 가능한 한 빠른 헤드리스 실행
- 특정 시점까지 실행
- 초기 상태로 리셋

### 4.1 고정 시간 간격 방식

```python
while running:
    engine.step(0.01)
```

항상 일정한 시간만큼 진행한다. 로봇 궤적, 이동체, 충돌과 같이 연속적인 상태 계산에 적합하다.

### 4.2 이산 사건 방식

```text
10.0초: 제품이 컨베이어 끝에 도착
10.2초: 센서 ON
10.3초: 로봇 작업 시작
12.7초: 로봇 작업 완료
```

다음 사건이 발생할 시간으로 곧바로 이동한다. 생산량, 대기열, 공정 완료와 물류 흐름을 계산할 때 효율적이다.

### 4.3 혼합 방식

공장 시뮬레이터는 두 방식을 함께 사용하는 경우가 많다.

- 로봇과 이동체: 고정 시간 간격
- 공정 완료와 PLC 신호: 이벤트
- 생산 통계와 물류 흐름: 이산 사건

초기 구현에서는 고정 시간 스텝을 기본으로 시작하고, 필요할 때 시간순 이벤트 큐를 추가하는 방법이 현실적이다.

## 5. 실행 순서

같은 시간 스텝 안에서도 처리 순서가 결과에 영향을 준다. 엔진은 System의 실행 순서를 중앙에서 결정해야 한다.

예를 들면 다음과 같다.

```text
1. 외부 명령 적용
2. 제어기 계산
3. 로봇과 컨베이어 동작
4. 물리 및 충돌 계산
5. 센서 상태 계산
6. 이벤트 생성
7. 결과 기록
```

```python
class SimulationEngine:
    def step(self, dt: float) -> None:
        self._apply_commands()
        self._control_system.update(self._world, dt)
        self._motion_system.update(self._world, dt)
        self._collision_system.update(self._world, dt)
        self._sensor_system.update(self._world, dt)
        self._publish_events()
        self._clock.advance(dt)
```

로봇이나 컨베이어가 임의로 다른 구성요소를 갱신하면 실행 순서가 암묵적으로 변하고 결과를 재현하기 어려워진다.

## 6. Command와 Event

명령과 이벤트는 방향과 의미가 다르므로 구분해야 한다.

### Command

외부 주체가 엔진에 수행을 요청하는 의도다.

```text
MoveRobot
StartConveyor
StopMachine
ResetAlarm
LoadFactory
```

Command는 아직 일어나지 않은 요청이므로 실패하거나 거절될 수 있다.

### Event

엔진 내부에서 이미 일어난 사실을 외부에 알리는 메시지다.

```text
RobotMotionCompleted
ProductArrived
SensorActivated
CollisionDetected
MachineFaulted
```

전체 흐름은 다음과 같다.

```text
UI / PLC / 외부 시스템
        │ Command
        ▼
SimulationEngine
        │
        ├── World 상태 변경
        └── Event 발생
                │
                ▼
         UI / Logger / PLC
```

이 구분은 UI, 네트워크 또는 PLC 프로토콜이 핵심 시뮬레이션 코드에 직접 침투하는 것을 방지한다.

## 7. 엔진의 경계

핵심 엔진은 다음을 직접 담당하지 않는 편이 좋다.

- GUI 렌더링
- 마우스와 키보드 입력 처리
- 프로젝트 파일 선택 UI
- 데이터베이스나 HTTP API 직접 접근
- 특정 3D 렌더러 구현
- 특정 PLC 통신 프로토콜 구현
- 운영체제 스레드나 소켓의 세부 처리

이 기능들은 엔진 바깥 계층에서 Command와 Event 또는 명시적인 포트를 통해 엔진에 연결한다.

```text
┌──────────────────────────────────────┐
│ UI / CLI / API Server                │
├──────────────────────────────────────┤
│ Application                          │
│ 프로젝트 로딩, 명령 변환, 저장       │
├──────────────────────────────────────┤
│ Simulation Engine                    │
│ 시간, World, Systems, Events         │
├──────────────────────────────────────┤
│ Domain                               │
│ Robot, Link, Joint, Conveyor, Sensor │
├──────────────────────────────────────┤
│ Math / Geometry / Utility            │
└──────────────────────────────────────┘
```

이 경계를 유지하면 GUI가 없어도 자동 테스트나 서버 환경에서 시뮬레이션을 실행할 수 있다.

## 8. 추상화 원칙

추상화는 모든 클래스에 인터페이스를 추가하는 작업이 아니다. 실제로 구현을 교체하거나 실행 순서를 조합해야 하는 경계에 적용해야 한다.

### 8.1 적절한 추상화 대상

System의 공통 실행 계약은 추상화할 가치가 있다.

```python
class SimulationSystem(Protocol):
    def initialize(self, world: World) -> None: ...
    def update(self, context: SimulationContext) -> None: ...
    def reset(self, world: World) -> None: ...
```

이 밖에도 다음 경계는 교체 가능성이 크다.

- 시뮬레이션 시간 제공자
- 이벤트 발행 대상
- 공장 정의 로더
- 물리 또는 충돌 구현
- 외부 제어기 어댑터
- 상태 저장소

```python
class EventSink(Protocol):
    def publish(self, event: SimulationEvent) -> None: ...


class FactoryLoader(Protocol):
    def load(self, source: str) -> FactoryDefinition: ...
```

### 8.2 과도한 추상화를 피할 대상

다음은 처음부터 인터페이스로 감쌀 필요가 없다.

- `Robot`, `Link`, `Joint`처럼 이미 역할이 명확한 도메인 모델
- 구현체가 하나뿐이고 교체 필요가 없는 작은 계산기
- 단순 컬렉션을 감싸기만 하는 manager 클래스
- 미래의 가능성만을 위해 만든 빈 추상 계층

`RobotManager`, `FactoryManager`, `SimulationManager`처럼 범위가 불명확한 이름보다 실제 책임을 드러내는 이름이 좋다.

```text
RobotMotionSystem
ComponentRegistry
EventScheduler
FactoryLoader
SimulationClock
```

## 9. 최소 엔진 인터페이스

초기 버전은 World와 System을 받아 한 스텝씩 실행하는 구조로 시작할 수 있다.

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SimulationContext:
    time: float
    dt: float


class SimulationSystem(Protocol):
    def update(self, world: World, context: SimulationContext) -> None: ...
    def reset(self, world: World) -> None: ...


class SimulationEngine:
    def __init__(
        self,
        world: World,
        systems: list[SimulationSystem],
    ):
        self._world = world
        self._systems = tuple(systems)
        self._time = 0.0

    @property
    def time(self) -> float:
        return self._time

    @property
    def world(self) -> World:
        return self._world

    def step(self, dt: float) -> None:
        if dt <= 0:
            raise ValueError("dt must be positive")

        context = SimulationContext(time=self._time, dt=dt)

        for system in self._systems:
            system.update(self._world, context)

        self._time += dt

    def reset(self) -> None:
        self._time = 0.0
        for system in self._systems:
            system.reset(self._world)
```

엔진을 반복 호출하는 실행 루프는 별도 객체로 분리할 수 있다.

```python
class SimulationRunner:
    def run(self) -> None:
        while self._running:
            self._engine.step(self._fixed_dt)
```

이때 역할은 다음과 같이 구분된다.

- `SimulationEngine.step()`: 상태를 정확히 한 단계 계산한다.
- `SimulationRunner`: 엔진을 언제, 얼마나 자주 호출할지 결정한다.

따라서 엔진 자체가 프로세스나 무한 루프일 필요는 없다. 이 구조에서는 테스트가 벽시계 시간이나 스레드에 의존하지 않는다.

```python
engine.step(0.01)
assert robot.joint(0).value == expected
```

## 10. 정의와 런타임 상태의 분리

공장 구성요소의 변하지 않는 설정과 실행 중 상태를 분리하면 저장, 복원과 테스트가 쉬워진다.

### Definition 또는 Specification

```python
@dataclass(frozen=True)
class RobotDefinition:
    model: str
    base_transform: Transform
    joint_limits: tuple[Range, ...]
```

### Runtime State

```python
@dataclass
class RobotState:
    joint_positions: list[float]
    joint_velocities: list[float]
    operating_mode: OperatingMode
    alarm: RobotAlarm | None
```

개념적으로 하나의 로봇은 다음 요소로 구성된다.

```text
Robot
├── Definition: 모델, 축 제한, 최대 속도
├── State: 현재 관절값, 동작 상태, 알람
└── Behavior: 명령 검증과 운동 계산
```

이 구분으로 다음 기능을 구현하기 쉬워진다.

- 초기 상태 생성과 리셋
- 공장 프로젝트 저장과 로딩
- 상태 복제와 스냅샷
- 실행 기록 재생
- 동일 조건 테스트

## 11. 중요한 품질 속성

### 11.1 결정성

같은 초기 상태, 같은 명령, 같은 시간 스텝을 사용하면 같은 결과가 나와야 한다.

```text
초기 상태 + 명령 순서 + 시간 스텝
                  ↓
               같은 결과
```

이를 위해 다음 요소를 통제해야 한다.

- System 실행 순서
- 시간 스텝 크기
- 난수 시드
- 동시성
- 외부 입력이 적용되는 시점
- 부동소수점 계산 정책

### 11.2 재현성과 리플레이

사용자 명령과 외부 신호를 시뮬레이션 시간과 함께 기록하면 동일한 실행을 재현하고 문제를 분석할 수 있다.

### 11.3 상태 스냅샷

특정 시점의 World를 저장하고 복구할 수 있으면 다음 기능이 가능하다.

- 일시정지와 복원
- 디버깅
- 실행 취소
- 시나리오 분기
- 장애 상황 재현

### 11.4 헤드리스 실행

GUI 없이 엔진을 실행할 수 있어야 자동 테스트, CI 및 대량 시뮬레이션이 가능하다.

### 11.5 명확한 상태 소유권

각 상태를 누가 변경할 수 있는지 명확해야 한다. 예를 들어 UI, PLC, `Robot`, `Kinematics`가 joint 값을 각각 직접 변경한다면 일관성을 보장하기 어렵다.

외부 주체는 Command를 보내고, 실제 상태 변경은 해당 상태를 책임지는 System 또는 도메인 객체가 수행하도록 제한하는 것이 좋다.

## 12. 현재 프로젝트에 적용하는 방향

현재 `station` 패키지의 `Robot`, `Link`, `Joint`, `Kinematics`는 엔진 자체보다는 로봇 도메인 모델과 계산 기능에 가깝다.

장기적으로는 다음과 같은 구조를 고려할 수 있다.

```text
station/
├── engine/
│   ├── engine.py
│   ├── clock.py
│   ├── context.py
│   ├── command.py
│   ├── event.py
│   ├── scheduler.py
│   └── system.py
├── world/
│   ├── world.py
│   └── component_registry.py
├── robot/
│   ├── robot.py
│   └── kinematics/
├── conveyor/
├── machine/
├── sensor/
└── process/
```

처음부터 모든 디렉터리와 추상화를 만들 필요는 없다. 최소 시작점은 다음 네 가지다.

1. `World`: 공장 구성요소를 보관한다.
2. `SimulationEngine.step(dt)`: 시간을 한 단계 진행한다.
3. `SimulationSystem`: 상태 변경 규칙의 실행 계약을 정의한다.
4. `SimulationEvent`: 엔진 내부에서 발생한 사실을 전달한다.

먼저 로봇과 컨베이어가 하나의 시간 스텝 안에서 움직이고 상호작용하는 작은 수직 기능을 구현한다. 이후 실제 요구가 생길 때 Command queue, event scheduler, snapshot, replay 기능을 추가하는 것이 좋다.

## 13. 요약

시뮬레이션 엔진은 거대한 만능 객체가 아니다.

> 엔진은 World의 상태를 직접 표현하는 객체라기보다, 시간과 실행 순서를 통제하면서 여러 도메인 규칙이 일관되게 상태를 변경하도록 조율하는 런타임이다.

공장 시뮬레이터의 첫 설계에서는 다음 원칙이 특히 중요하다.

- 시뮬레이션 시간과 현실 시간을 분리한다.
- Component의 상태와 System의 실행 규칙을 구분한다.
- System 실행 순서를 엔진이 중앙에서 통제한다.
- Command와 Event를 구분한다.
- GUI와 통신 기능을 핵심 엔진 밖에 둔다.
- 정의 데이터와 런타임 상태를 분리한다.
- 결정성과 헤드리스 테스트를 초기부터 고려한다.
- 실제 교체 지점에만 추상화를 도입한다.
