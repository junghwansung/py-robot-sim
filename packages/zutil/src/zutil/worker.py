"""
Worker / PeriodicWorker / CancellableOneShotTimer

스레드 생명주기 추상화 유틸리티.
threading.Thread 직접 사용 금지 — 이 클래스를 통해 사용.

Usage:
    from utils.worker import Worker, PeriodicWorker, CancellableOneShotTimer

    # 단발성 / 자체 루프 태스크 — stop_event를 받아 우아하게 종료
    def run_server(host: str, port: int, stop_event: threading.Event) -> None:
        while not stop_event.is_set():
            ...

    worker = Worker(target=lambda: run_server("localhost", 5555), name="ZmqServer")
    worker.start()
    worker.stop()

    # 주기적 반복 태스크 — 파라미터가 있는 함수는 lambda로 감쌈
    def check_plc_status(plc_ip: str, timeout: float) -> None:
        ...

    periodic = PeriodicWorker(
        target=lambda: check_plc_status("192.168.1.10", 1.0),
        interval=0.1,
        name="PlcMonitor",
    )
    periodic.start()
    periodic.stop()
"""

import inspect
import threading
import traceback
from typing import Callable

_JOIN_TIMEOUT_SEC: float = 5.0


class Worker:
    """단발성/자체루프 태스크를 위한 스레드 래퍼.

    target 함수를 별도 스레드에서 한 번 실행한다.
    장시간 실행되는 target(서버 루프 등)은 내부에서 stop_event를 받아
    스스로 종료해야 한다.

    Args:
        target: 스레드에서 실행할 함수. `stop_event: threading.Event` 키워드
                인자를 받으면 자동으로 전달되어 우아한 종료가 가능하다.
        name: 로그·디버그용 스레드 이름.
        daemon: True(기본)면 메인 프로세스 종료 시 함께 종료된다.
    """

    def __init__(
        self,
        target: Callable[..., None],
        name: str,
        daemon: bool = True,
    ) -> None:
        self._target = target
        self._name = name
        self._daemon = daemon
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    # ── 라이프사이클 ──

    def start(self) -> None:
        """스레드를 시작한다. 이미 실행 중이면 무시한다."""
        if self._thread is not None and self._thread.is_alive():
            print(f"[{self._name}] 이미 실행 중입니다.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name=self._name,
            daemon=self._daemon,
        )
        self._thread.start()
        print(f"[{self._name}] 시작됨.")

    def stop(self) -> None:
        """stop_event를 설정하고 스레드가 종료될 때까지 최대 join timeout 만큼 대기한다."""
        self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=_JOIN_TIMEOUT_SEC)
            if self._thread.is_alive():
                print(f"[{self._name}] {_JOIN_TIMEOUT_SEC}초 내에 종료되지 않았습니다.")
            else:
                print(f"[{self._name}] 정상 종료됨.")

    def is_alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    # ── 내부 ──

    def _run(self) -> None:

        try:
            sig = inspect.signature(self._target)
            if "stop_event" in sig.parameters:
                self._target(stop_event=self._stop_event)
            else:
                self._target()
        except Exception as e:  # pylint: disable=broad-except
            print(f"[{self._name}] 예외 발생: {e}\n{traceback.format_exc()}")


class PeriodicWorker:
    """일정 주기로 target 함수를 반복 호출하는 스레드 래퍼.

    Args:
        target: 주기마다 호출할 함수.
        interval: 호출 간격 (초). 이전 호출 종료 후 interval 만큼 대기한다.
        name: 로그·디버그용 스레드 이름.
        daemon: True(기본)면 메인 프로세스 종료 시 함께 종료된다.
    """

    def __init__(
        self,
        target: Callable[..., None],
        interval: float,
        name: str,
        daemon: bool = True,
    ) -> None:
        self._target = target
        self._interval = interval
        self._name = name
        self._daemon = daemon
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    # ── 라이프사이클 ──

    def start(self) -> None:
        """스레드를 시작한다. 이미 실행 중이면 무시한다."""
        if self._thread is not None and self._thread.is_alive():
            print(f"[{self._name}] 이미 실행 중입니다.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name=self._name,
            daemon=self._daemon,
        )
        self._thread.start()
        print(f"[{self._name}] 시작됨 (interval={self._interval}s).")

    def stop(self) -> None:
        """반복 루프를 중단하고 스레드가 종료될 때까지 대기한다."""
        self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=_JOIN_TIMEOUT_SEC)
            if self._thread.is_alive():
                print(f"[{self._name}] {_JOIN_TIMEOUT_SEC}초 내에 종료되지 않았습니다.")
            else:
                print(f"[{self._name}] 정상 종료됨.")

    def is_alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    # ── 내부 ──

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._target()
            except Exception as e:  # pylint: disable=broad-except
                print(f"[{self._name}] 예외 발생: {e}\n{traceback.format_exc()}")
            self._stop_event.wait(timeout=self._interval)
