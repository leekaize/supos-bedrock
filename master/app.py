import docker
from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)
client = docker.from_env()

SERVICES_PROJECT = "supos-services"
SERVICES_COMPOSE = "/services/docker-compose.yml"

@app.route("/")
def dashboard():
    """Render main dashboard"""
    return render_template("dashboard.html")

@app.route("/api/status")
def get_status():
    """Get status of all services"""
    try:
        # Get master container status
        master = client.containers.get("supos-bedrock-master")
        master_status = master.status
        
        # Get service containers
        services = []
        try:
            postgres = client.containers.get("supos-postgres")
            services.append({
                "name": "postgres",
                "status": postgres.status,
                "health": "healthy" if postgres.status == "running" else "unhealthy"
            })
        except docker.errors.NotFound:
            services.append({
                "name": "postgres",
                "status": "not_started",
                "health": "unknown"
            })
        
        return jsonify({
            "master": {"status": master_status},
            "services": services
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/services/start", methods=["POST"])
def start_services():
    """Start service stack using docker compose"""
    try:
        # Use docker-compose command
        os.system(f"cd /services && docker-compose up -d")
        return jsonify({"message": "Services starting"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/services/stop", methods=["POST"])
def stop_services():
    """Stop service stack"""
    try:
        os.system(f"cd /services && docker-compose down")
        return jsonify({"message": "Services stopped"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)