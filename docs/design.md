# 설계 및 컨벤션

본 문서는 서버 설계 개요와 코드 컨벤션을 설명한다.

## Petstore

샘플이다.

## 컨벤션

### 내부 전용 라우팅
- 내부 전용 라우팅은 `/.internal/` 내에 둡니다. 예: health probes.

### 엔티티 식별자 타입
* 엔티티의 식별자는 기저 타입 - int나 str 등을 직접 사용하지 않고 Type alias를 걸어 사용한다. 예: `PetId`.
* 확장을 고려하여 직렬화되어 서버에서 외부로 반환하거나 입력 받을 때는 문자열(str)로 표현한다. 현재 int를 사용하더라도 나중에 uuid 등으로 전환해도 외부 API 인터페이스는 변경되지 않도록 한다.

### 빈 응답
- 빈 응답은 204 No Content가 아닌 200 OK + `{}` (EmptyResponse)를 사용한다.

### 응답의 Top-level 자료형
* 항상 객체여야 한다. 스칼라나 리스트가 되면 확장이 어렵다.
* 목록/검색 API에서는 `ListResponse[T]`를 사용한다.
* TODO: 페이지네이션 이 생기면 `PageResponse[T]`를 추가해 페이징 필드를 확장할 예정.

### 오류 응답
* [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html) Problem Details for HTTP APIs 규격을 사용한다.
* Validation 오류는 422가 아닌 400 응답 코드를 사용한다.
* 서버 내부 오류는 외부에 세부를 노출하지 않고 500 Internal Server Error만 반환한다.

### Pydantic 모델
* 필드의 부재를 표현하기 위해 Pydantic의 `MISSING` sentinel을 사용한다. 다만 이는 2.12.0a1 이상에서 제공되며, mypy 지원이 아직 부족하여 `# type: ignore` 주석이 필요했습니다.
