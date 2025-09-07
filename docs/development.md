# 개발 환경 가이드

본 문서는 로컬 개발을 위한 최소 가이드를 제공한다. 상세 설계/컨벤션은 docs/design.md 참조.

## 주요 기술 스택

* Python 3.12+
* [uv](https://docs.astral.sh/uv/) (Python 패키지/가상환경 매니저)
* [FastAPI](https://fastapi.tiangolo.com/), [uvicorn](https://www.uvicorn.org/)

### 개발 서버 구동

```bash
uv run uvicorn --reload --port 8080 python_toy.server.app:create_app
```

혹은, 아직 작업중인 실 서버 Entrypoint를 테스트하고 싶다면

```bash
uv run server
```

DI 컨테이너(`Container`)는 `create_app()`에서 생성되며, FastAPI `app.state.container`에 노출됩니다. 라우터/서비스는 Request를 통해 컨테이너에서 인스턴스를 꺼내 사용한다.

애플리케이션 라이프사이클은 FastAPI lifespan 훅으로 관리되며, 시작 시 health startup 플래그를 올리고, 종료 시 readiness를 내린 뒤 DI 리소스를 정리한다.

## 로컬 PC 설정

### 환경변수 구성

애플리케이션 설정은 pydantic-settings를 통해 환경변수로 주입된다. 접두사는 `APP_`, 중첩 구분자는 `.`이다.

* .env.example 샘플을 .env로 복사해서 개인별 설정은 여기에 설정할 것
* 지원 키: `src/python_toy/server/infra/config.py` 참조

### 의존성 설치(최초 1회 또는 변경 시)

```bash
uv sync --group dev
```

### Lint: ruff

```bash
uv run ruff check
```

### Type checking: mypy

```bash
uv run mypy
```

### Test: pytest

```bash
uv run pytest
```

## .gitignore

저장소 루트 /.gitignore 에는 개인 취향에 따른 플랫폼, IDE별 설정을 포함하지 않는다.
각자 알아서 Global .gitignore 를 설정하고. 방법도 각자 찾아볼 것.

참고로 플랫폼/IDE별로 무시 대상이 될 수 있는 예시: Thumbs.db, .DS_Store, /.vscode/, /.idea/ 등이 있다. 이러한 항목을 레포지토리의 .gitignore 에 추가하거나 가비지를 커밋하지 말고 개인 Global ignore로 처리할 것.
