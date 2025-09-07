# VS Code 설정 예시

이 문서는 AI가 생성함

`.vscode` 디렉토리는 gitignore 대상이므로 커밋되지 않는다. 아래 예시를 참고해 개인 PC에 설정.

## tasks.json 예시

다음은 uv 가상환경(.venv)을 사용해 ruff/mypy/pytest를 실행하는 Task 예시

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "ruff",
            "type": "shell",
            "command": "uv",
            "args": ["run", "ruff", "check"],
            "options": {
                "env": {
                    "UV_PYTHON": "${workspaceFolder}/.venv/bin/python"
                }
            }
        },
        {
            "label": "mypy",
            "type": "shell",
            "command": "uv",
            "args": ["run", "mypy"],
            "options": {
                "env": {
                    "UV_PYTHON": "${workspaceFolder}/.venv/bin/python"
                }
            }
        },
        {
            "label": "pytest",
            "type": "shell",
            "command": "uv",
            "args": ["run", "pytest"],
            "options": {
                "env": {
                    "UV_PYTHON": "${workspaceFolder}/.venv/bin/python"
                }
            },
            "group": {
                "kind": "test",
                "isDefault": true
            }
        }
    ]
}
```

## launch.json 예시 (애플리케이션 실행/디버그)


```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: FastAPI",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": ["--port", "8080", "--reload", "python_toy.server.app:create_app"]
        }
    ]
}
```
