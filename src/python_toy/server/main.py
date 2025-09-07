import click
import uvicorn


@click.command()
@click.option("--host", default="")
@click.option("--port", default="8080", type=int)
def start_server(host: str, port: int) -> None:
    from python_toy.server.app import create_app  # noqa: PLC0415

    app = create_app()

    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        loop="uvloop",
        log_level="info",
        log_config=None,  # Use our logger.
    )
    server = uvicorn.Server(config)
    server.run()


def main() -> None:
    start_server()


if __name__ == "__main__":
    main()
