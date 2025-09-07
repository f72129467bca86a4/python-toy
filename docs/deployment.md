# 배포 가이드

**TODO**

## Health Check Probes 및 API

서비스는 다음 내부 라우트를 제공한다. 운영 환경의 헬스 프로브에 연결하세요. 이 엔드포인트들은 OpenAPI 스키마에 노출되지 않습니다.

* `/.internal/healthz/liveness`: 프로세스 생존 여부. 항상 UP을 반환한다.
* `/.internal/healthz/startup`: 애플리케이션 시작 완료 여부. 시작 전에는 503, 시작 후에는 200을 반환한다.
* `/.internal/healthz/readiness`: 트래픽 수용 가능 여부. 시작 전/종료 중에는 503, 정상 동작 시 200을 반환한다.

응답 본문은 text/plain 으로 200 OK + "UP || 503 Service Unavailable + "DOWN"
