import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / '.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ro_studio.settings')

# Parse arguments passed by supervisor or npm run dev
port = '3000'
host = '0.0.0.0'

args = sys.argv[1:]
i = 0
while i < len(args):
    arg = args[i]
    if arg == '--port' and i + 1 < len(args):
        port = args[i + 1]
        i += 2
        continue
    elif arg.startswith('--port='):
        port = arg.split('=', 1)[1]
    elif arg == '--host' and i + 1 < len(args):
        host = args[i + 1]
        i += 2
        continue
    elif arg.startswith('--host='):
        host = arg.split('=', 1)[1]
    i += 1

import django
django.setup()
from django.core.management import call_command

try:
    call_command('migrate', interactive=False)
    call_command('seed_data', interactive=False)
except Exception as e:
    print(f"Startup DB check: {e}")

addr = f"{host}:{port}"
print(f"🚀 Iniciando servidor Django para Ro Studio en http://{addr}/")
call_command('runserver', addr, use_reloader=False)
