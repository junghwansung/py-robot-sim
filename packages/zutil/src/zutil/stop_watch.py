import time


class StopWatch:
    """
    시간 측정을 위한 StopWatch 클래스
    - start(): StopWatch 시작 또는 재개
    - lap(): StopWatch 중간 측정 - 마지막 측정 이후 경과 시간 반환
    - num_laps(): 측정 횟수 반환
    - stop(): StopWatch 정지 - 현재까지의 경과 시간 반환 (start로 재개 가능)
    - duration_from_start(): 시작부터의 총 경과 시간 반환 (실행 중이든 정지 중이든)
    - is_running(): StopWatch 실행 중 여부 반환
    - get_lap_times(): 모든 lap time 리스트 반환
    - get_lap_time_by_index(index): 특정 인덱스의 lap 시간 반환

    사용 예시:
    stopwatch = StopWatch()

    1. 두 번의 lap 측정과 정지까지의 전체 경과 시간 측정
    stopwatch.start() -> stopwatch.lap() -> stopwatch.lap() -> stopwatch.stop()
    stopwatch.duration_from_start()

    2. 정지 후 재개하여 추가 측정
    stopwatch.start() -> stopwatch.lap() -> stopwatch.stop() -> stopwatch.start()

    3. n번의 lap 측정과 각 lap 시간 조회
    stopwatch.start() -> stopwatch.lap() -> stopwatch.lap() -> ... -> stopwatch.stop()
    stopwatch.get_num_laps() -> stopwatch.get_lap_time_by_index(0) -> stopwatch.get_lap_time_by_index(1)
    """

    def __init__(self) -> None:
        self._start_time: float | None = None
        self._last_time: float | None = None
        self._stop_time: float | None = None
        self._lap_times: list[float] = []
        self._is_running: bool = False

    def reset(self) -> None:
        """StopWatch 초기화"""
        self._start_time = None
        self._last_time = None
        self._stop_time = None
        self._lap_times.clear()
        self._is_running = False

    def start(self) -> None:
        """StopWatch 시작 또는 재개"""
        if self._is_running:
            return  # 이미 실행 중이면 아무것도 하지 않음

        current_time = time.monotonic()

        if self._stop_time is not None and self._start_time is not None:
            # 정지된 상태에서 재개하는 경우 - 시간 보정
            pause_duration = current_time - self._stop_time
            self._start_time += pause_duration
            if self._last_time is not None:
                self._last_time += pause_duration
            self._stop_time = None
        else:
            # 처음 시작하는 경우
            self._start_time = current_time

        self._is_running = True

    def lap(self) -> float | None:
        """StopWatch 중간 측정 - 마지막 측정 이후 경과 시간 반환"""
        if not self._is_running or self._start_time is None:
            return None

        current_time: float = time.monotonic()
        duration_from_last: float = current_time - (self._last_time or self._start_time)
        self._last_time = current_time
        self._lap_times.append(duration_from_last)
        return duration_from_last

    @property
    def num_laps(self) -> int:
        """측정 횟수 반환"""
        return len(self._lap_times)

    @property
    def is_running(self) -> bool:
        """StopWatch 실행 중 여부 반환"""
        return self._is_running

    def stop(self) -> float | None:
        """StopWatch 정지 - 현재까지의 경과 시간 반환 (start로 재개 가능)"""
        if not self._is_running or self._start_time is None:
            return None

        self._stop_time = time.monotonic()
        self._is_running = False
        return self._stop_time - self._start_time

    def duration_from_start(self) -> float | None:
        """시작부터의 총 경과 시간 반환 (실행 중이든 정지 중이든)"""
        if self._start_time is None:
            return None

        if self._is_running:
            return time.monotonic() - self._start_time
        elif self._stop_time is not None:
            return self._stop_time - self._start_time
        else:
            return None

    def get_lap_time_by_index(self, index: int) -> float | None:
        """특정 인덱스의 lap 시간 반환"""
        if 0 <= index < len(self._lap_times):
            return self._lap_times[index]
        return None


class StopWatchManager:
    """
    여러 StopWatch 인스턴스를 관리하는 매니저 클래스
    """

    def __init__(self) -> None:
        self._stopwatches: dict[str, StopWatch] = {}

    def get_stopwatch(self, name: str) -> StopWatch | None:
        """이름으로 StopWatch 인스턴스 반환 (없으면 None)"""
        if name not in self._stopwatches:
            return None
        return self._stopwatches[name]

    def create_stopwatch(self, name: str) -> StopWatch:
        """이름에 해당하는 StopWatch 인스턴스 생성 및 반환 (이미 존재하면 기존 인스턴스 반환)"""
        if name not in self._stopwatches:
            self._stopwatches[name] = StopWatch()
        return self._stopwatches[name]

    def delete_stopwatch(self, name: str) -> None:
        """이름에 해당하는 StopWatch 인스턴스 삭제"""
        if name in self._stopwatches:
            del self._stopwatches[name]
