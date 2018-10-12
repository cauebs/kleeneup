from cleo import Application

from .cli import fa, re, rg

application = Application()

application.add_commands(fa.commands)
application.add_commands(rg.commands)
application.add_commands(re.commands)

application.run()
