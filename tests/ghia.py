import click


@click.command()
@click.option('-s',
              '--strategy',
              type=click.Choice(['append', 'set', 'change']),
              default="append",
              help='How to handle assignment collisions.'
              )
@click.option('-d',
              '--dry-run',
              default="append",
              help='Run without making any changes.'
              )
@click.argument('-a',
                '--config-auth',
                default="credentials.cfg",
                help='File with authorization configuration.',
                required=True
                )
@click.argument('-r',
                '--config-rules',
                default="credentials.cfg",
                help='File with assignment rules configuration.',
                required=True
                )
def run():
    return
