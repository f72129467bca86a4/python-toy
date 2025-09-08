# 설계 및 컨벤션

본 문서는 서버 설계 개요와 코드 컨벤션을 설명한다.

## Petstore

샘플이다.

## DI(Dependency Injection)

본 프로젝트는 [dependency-injector](https://python-dependency-injector.ets-labs.org/)를 사용한다.

* 컨테이너 정의: `python_toy.server.infra.container.Container` 참조
* FastAPI에서는 `create_app()`에서 컨테이너를 생성하고 `app.state.container`에 저장한다.

## 컨벤션

### 1 파일 1 클래스(One-file-one-class)

1 파일에 대표 클래스는 1개만 둔다. 해당 대표 클래스가 참조하는 보조 클래스 정도는 같이 있을 수 있다.

### 내부 전용 라우팅

* 내부 전용 라우팅은 `/.internal/` 내에 둔다. ex) `/.internal/healthz/ready`

### 엔티티 식별자 타입

* 엔티티의 식별자는 기저 타입 - int나 str 등을 직접 사용하지 않고 Type alias를 걸어 사용한다. 예: `PetId`.
* 확장을 고려하여 직렬화되어 서버에서 외부로 반환하거나 입력 받을 때는 문자열(str)로 표현한다. 현재 int를 사용하더라도 나중에 uuid 등으로 전환해도 외부 API 인터페이스는 변경되지 않도록 한다.

### 빈(Empty) 응답

* 빈 응답은 204 No Content가 아닌 200 OK + `{}` (EmptyResponse)를 사용한다.

### 응답의 Top-level 자료형

* 항상 객체여야 한다. 스칼라나 리스트가 되면 확장이 어렵다.
* 목록/검색 API에서는 페이징 필요 여부에 따라 `PageResponse[T]` 또는 `ListResponse[T]` 를 사용한다.

### 오류 응답

* [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html) Problem Details for HTTP APIs 규격을 사용한다.
* Validation 오류는 422가 아닌 400 응답 코드를 사용한다.
* 서버 내부 오류는 외부에 세부를 노출하지 않고 500 Internal Server Error만 반환한다.

### MISSING Sentinel

필드의 부재를 표현하기 위해 Pydantic의 `MISSING` sentinel을 사용한다. 다만 이는 Pydantic 2.12.0a1 이상에서 제공되며, mypy 지원이 아직 부족하여 Workaround가 필요.

* 배경: [PEP 661 – Sentinel Values](https://peps.python.org/pep-0661/)
* Pydantic Docs: [MISSING sentinel](https://docs.pydantic.dev/dev/concepts/experimental/#missing-sentinel)
* [Stabilize MISSING sentinel feature #12090](https://github.com/pydantic/pydantic/issues/12090)

Workaround:

* `variable is NOT MISSING # type: ignore[comparison-overlap]`
* 모델 선언시:
```py
class ExampleModel(BaseModel):
    name: str | MISSING  # type: ignore[valid-type]
```


## FastAPI

### 라우팅

`APIRoute(prefix="/v1/resource")` 는 사용하지 말고 `@route(path=/v1/resource")` 형태로 route 별로 path를 명시한다.

중복 코드는 생기지만 단순한 grep 로도 라우팅을 빠르게 찾아낼 수 있다.

### FastAPI 계층 DI

`APIRouter` 내에서 다음 의존성 헬퍼를 사용한다.

```py
def _pet_repo_dep(request: Request) -> InMemoryPetRepository:
		container: Container = request.app.state.container
		return container.pet_repository()
```

이 방식은 스타트업 시점의 컨테이너를 재사용하고 테스트에서도 동일하게 동작한다.

### CBV(@cbv) 기반 라우팅

웹 계층을 클래스 형태로 표현하기 위해 [fastapi-utils의 @cbv](https://fastapi-utils.davidmontague.xyz/user-guide/class-based-views/)를 사용한다.

핵심 요점:

* 웹 라우트 클래스(`PetRoutes`)는 `@cbv(router)`로 선언하고, 속성에 `Depends`로 Repository/Service를 주입한다.

예시 요약:

```python
router = APIRouter(tags=["pets"])

def _pet_repo_dep(request: Request) -> InMemoryPetRepository:
	container: Container = request.app.state.container
	return container.pet_repository()

@cbv(router)
class PetRoutes:
	repo: InMemoryPetRepository = Depends(_pet_repo_dep)

	@router.post("/v1/pets", status_code=201)
	async def create_pet(self, payload: PetCreate) -> Pet:
		return await self.repo.create(payload)
```

이 패턴은 Spring의 클래스형 컨트롤러와 유사한 구조를 제공하면서, DI 컨테이너와의 순환 의존을 피한다.


## 디렉터리 구조

```
├── pyproject.toml
├── uv.lock
├── mypy.ini
├── ruff.toml
├── docs
│   ├── design.md
│   └── ...
├── src
│   ├── tests : Test root
│   │   ├── conftest.py
│   │   ├── test_errors.py
│   │   ├── test_health_probes.py
│   │   └── ...
│   ├── python_toy : Root package
│
└── ...
```
