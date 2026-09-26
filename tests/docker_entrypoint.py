"""Run the container entrypoint with filesystem and process boundaries stubbed."""

import os
import subprocess
import tempfile
from pathlib import Path


def run_entrypoint(
    entrypoint: Path,
    environment: dict[str, str],
    commands: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="mealie-entry-test-") as directory:
        root = Path(directory)
        app = root / "app"
        app.mkdir()
        activate = root / "activate"
        activate.write_text("")
        bin_dir = root / "bin"
        bin_dir.mkdir()
        stubs = {
            "id": "echo 911\n",
            "ip": "echo 'default via 172.20.0.1 dev eth0'\n",
            "mealie": (
                "echo APP_STARTED\n"
                "printf 'HOST_IP=%s\\n' \"${HOST_IP-UNSET}\"\n"
                "printf 'POSTGRES_PASSWORD=%s\\n' \"${POSTGRES_PASSWORD-UNSET}\"\n"
                "printf 'SMTP_PASSWORD=%s\\n' \"${SMTP_PASSWORD-UNSET}\"\n"
            ),
        }
        stubs.update(commands or {})
        for name, body in stubs.items():
            path = bin_dir / name
            path.write_text("#!/bin/bash\n" + body)
            path.chmod(0o755)

        # Redirect only absolute container paths; execute the real startup logic.
        source = entrypoint.read_text()
        source = source.replace("/opt/mealie/bin/activate", str(activate))
        source = source.replace("/sbin/ip", str(bin_dir / "ip"))
        source = source.replace("/app", str(app))
        script = root / "entry.sh"
        script.write_text(source)
        return subprocess.run(
            ["/bin/bash", str(script)],
            env={"PATH": f"{bin_dir}:{os.defpath}", "PUID": "911", "PGID": "911", **environment},
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
