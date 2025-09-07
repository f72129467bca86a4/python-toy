from __future__ import annotations

from http import HTTPStatus
from typing import Any, Mapping

from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

MEDIA_TYPE = "application/problem+json"


class ProblemDetails(BaseModel):
    """RFC 9457 Problem Details for HTTP APIs 모델.

    필드 정의 (RFC 9457):
      - type: 문제 타입을 식별하는 URI (기본값: "about:blank")
      - title: 짧고 사람이 읽기 쉬운 요약 (type이 about:blank이면 HTTP status phrase 사용)
      - status: HTTP 상태 코드 (오류 발생 시의 값)
      - detail: 사람이 읽기 쉬운 상세 설명 (선택)
      - instance: 이 문제 발생 인스턴스를 식별하는 URI (선택)
    추가 확장 속성은 RFC에 따라 허용된다.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    type: str = Field(default="about:blank")
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None

    # 확장 필드는 extra 로 허용

    def as_dict(self) -> dict[str, Any]:  # 편의 메서드
        return self.model_dump(exclude_none=True)


def _default_title(status: int) -> str:
    try:
        return HTTPStatus(status).phrase
    except ValueError:
        return str(status)


def new_problem(
    *,
    status: int,
    detail: str | None = None,
    type: str = "about:blank",  # noqa: A002
    title: str | None = None,
    instance: str | None = None,
    extensions: Mapping[str, Any] | None = None,
) -> ProblemDetails:
    """ProblemDetails 인스턴스 생성 헬퍼.

    Unknown / 확장 필드는 extensions 로 전달.
    title 미지정 시 type == about:blank -> HTTP status phrase, 그 외에는 type 문자열의 마지막 path 조각을 fallback으로 사용.
    """
    if title is None:
        if type == "about:blank":
            title = _default_title(status)
        else:
            # type URI의 마지막 세그먼트 혹은 전체 문자열을 기본 제목으로
            tail = type.rstrip("/").rsplit("/", 1)[-1]
            title = tail.replace("-", " ") or _default_title(status)
    data: dict[str, Any] = {
        "type": type,
        "title": title,
        "status": status,
    }
    if detail is not None:
        data["detail"] = detail
    if instance is not None:
        data["instance"] = instance
    if extensions:
        # status, title 등 표준 필드와 겹치면 무시 (표준 우선)
        for k, v in extensions.items():
            if k not in data:
                data[k] = v
    return ProblemDetails(**data)


def problem_response(
    *,
    status: int,
    detail: str | None = None,
    type: str = "about:blank",  # noqa: A002
    title: str | None = None,
    instance: str | None = None,
    extensions: Mapping[str, Any] | None = None,
) -> JSONResponse:
    problem = new_problem(
        status=status,
        detail=detail,
        type=type,
        title=title,
        instance=instance,
        extensions=extensions,
    )
    return JSONResponse(
        status_code=problem.status,
        content=problem.model_dump(exclude_none=True),
        media_type=MEDIA_TYPE,
    )


__all__ = ["ProblemDetails", "new_problem", "problem_response"]
