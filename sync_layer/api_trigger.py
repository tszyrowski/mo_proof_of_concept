from flask import Flask, request
import subprocess
import os

app = Flask(__name__)


@app.route("/trigger-sync", methods=["GET", "POST"])
def trigger_sync():
    # Only trigger sync if it's a POST request
    if request.method == "POST":
        # Expand the tilde to the full path
        python_path = os.path.expanduser(
            "~/workspace_interview/mo_proof_of_concept/venv/vMO_3.12/bin/python"
        )
        sync_script_path = os.path.expanduser(
            "~/workspace_interview/mo_proof_of_concept/sync_layer/sync_db.py"
        )

        result = subprocess.run(
            [python_path, sync_script_path], capture_output=True, text=True
        )
        if result.returncode == 0:
            return "Sync successful", 200
        else:
            return f"Sync failed: {result.stderr}", 500
    else:
        return "This endpoint accepts POST requests to trigger sync.", 200


if __name__ == "__main__":
    app.run(debug=True, port=10000)
