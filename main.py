"""Lightyear
"""


if __name__ == '__main__':

    import argparse
    from lightyear.core import config, engine, logger


    parser = argparse.ArgumentParser(
        prog='lightyear',
        description='Pipeline runner'
    )
    subparsers = parser.add_subparsers(dest='client')

    parser.add_argument(
        '-l',
        '--log-level',
        help='set the logging level (default: info)',
        choices=['error','warning','info','debug'],
        default='info',
    )

    client_parsers = {}
    for name, client in config.clients.items():
        client_parsers[name] = subparsers.add_parser(name)
        for args, kwargs in client.args:
            client_parsers[name].add_argument(*args, **kwargs)

    args = parser.parse_args()
    logger.set_level(args.log_level)
    client_config = config.clients[args.client]
    engine.run(client_config, args)

