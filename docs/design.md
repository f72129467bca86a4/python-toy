# 설계 및 컨벤션

본 문서는 서버 설계 개요와 코드 컨벤션을 설명한다.

## Petstore

샘플이다.

## DI(Dependency Injection)

본 프로젝트는 [dependency-injector](https://python-dependency-injector.ets-labs.org/)를 사용한다.

* 컨테이너 정의: `python_toy.server.infra.container.Container`
* 프로바이더:
  - `settings`: `get_settings()` 싱글톤
  - `pet_repository`: `InMemoryPetRepository` 싱글톤

* 애플리케이션에서는 `create_app()`에서 컨테이너를 생성하고 `app.state.container`에 저장한다.

### FastAPI 통합 패턴

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

* 웹 라우트 클래스(`PetRoutes`)는 `@cbv(router)`로 선언하고, 속성에 `Depends`로 Repository를 주입한다.

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

## 컨벤션

### 내부 전용 라우팅

* 내부 전용 라우팅은 `/.internal/` 내에 둔다. ex) `/.internal/healthz/ready`

### 엔티티 식별자 타입

* 엔티티의 식별자는 기저 타입 - int나 str 등을 직접 사용하지 않고 Type alias를 걸어 사용한다. 예: `PetId`.
* 확장을 고려하여 직렬화되어 서버에서 외부로 반환하거나 입력 받을 때는 문자열(str)로 표현한다. 현재 int를 사용하더라도 나중에 uuid 등으로 전환해도 외부 API 인터페이스는 변경되지 않도록 한다.

### 빈 응답

* 빈 응답은 204 No Content가 아닌 200 OK + `{}` (EmptyResponse)를 사용한다.

### 응답의 Top-level 자료형

* 항상 객체여야 한다. 스칼라나 리스트가 되면 확장이 어렵다.
* 목록/검색 API에서는 `ListResponse[T]`를 사용한다.
* TODO: 페이지네이션 이 생기면 `PageResponse[T]`를 추가해 페이징 필드를 확장할 예정.

### 오류 응답

* [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html) Problem Details for HTTP APIs 규격을 사용한다.
* Validation 오류는 422가 아닌 400 응답 코드를 사용한다.
* 서버 내부 오류는 외부에 세부를 노출하지 않고 500 Internal Server Error만 반환한다.

### Pydantic 모델

* 필드의 부재를 표현하기 위해 Pydantic의 `MISSING` sentinel을 사용한다. 다만 이는 2.12.0a1 이상에서 제공되며, mypy 지원이 아직 부족하여 `# type: ignore` 주석이 필요.
