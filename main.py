"""Lightyear
"""


if __name__ == "__main__":

    import argparse

    from lightyear.core import config, engine, logger

    parser = argparse.ArgumentParser(prog="lightyear", description="Pipeline runner")
    subparsers = parser.add_subparsers(dest="client")

    parser.add_argument(
        "-l",
        "--log-level",
        help="set the logging level (default: info)",
        choices=["error", "warning", "info", "debug"],
        default="info",
    )

    client_parsers = {}
    for client_name, client_config in config.clients.items():
        client_parsers[client_name] = subparsers.add_parser(client_name)
        for args, kwargs in client_config.args:
            client_parsers[client_name].add_argument(*args, **kwargs)

    args = parser.parse_args()
    logger.set_level(args.log_level)

    try:
        client_config = config.clients[args.client]
        engine.run(client_config, args)
    except Exception as e:
        print("Error:", e)
        parser.print_help()
