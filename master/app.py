import docker
from flask import Flask, render_template, jsonify, request, redirect, url_for
import os
import setup_wizard

app = Flask(__name__)
client = docker.from_env()

SERVICES_PROJECT = "supos-services"
SERVICES_COMPOSE = "/services/docker-compose.yml"


# ==================== MIDDLEWARE ====================

@app.before_request
def check_first_run():
    """Redirect to setup wizard if first run (except setup routes)."""
    if setup_wizard.is_first_run():
        # Allow setup routes through
        if request.path.startswith('/setup') or request.path.startswith('/api/setup'):
            return None
        # Redirect everything else to setup
        return redirect(url_for('setup_page'))


# ==================== SETUP ROUTES ====================

@app.route("/setup")
def setup_page():
    """Render first-run setup wizard."""
    if not setup_wizard.is_first_run():
        return redirect(url_for('dashboard'))
    return render_template("setup.html")


@app.route("/api/setup/validate", methods=["POST"])
def validate_setup():
    """Validate system requirements for setup."""
    try:
        valid, issues, warnings = setup_wizard.validate_system_requirements()
        
        return jsonify({
            "valid": valid,
            "issues": issues,
            "warnings": warnings
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/setup/complete", methods=["POST"])
def complete_setup():
    """Complete setup wizard and save configuration."""
    try:
        data = request.get_json()
        
        # Load default config
        config = setup_wizard.load_config()
        
        # Create admin user
        admin_data = data.get('admin', {})
        config['admin'] = setup_wizard.create_admin_user(
            username=admin_data.get('username'),
            email=admin_data.get('email'),
            password=admin_data.get('password')
        )
        
        # Update network config
        network_data = data.get('network', {})
        config['network']['domain'] = network_data.get('domain')
        config['network']['port'] = network_data.get('port')
        
        # Update language
        language = data.get('language', 'en-US')
        config['localization']['language'] = language
        
        # Generate secure service passwords
        service_passwords = setup_wizard.generate_service_passwords()
        config['services']['postgres']['password'] = service_passwords['postgres']
        config['services']['keycloak']['admin_password'] = service_passwords['keycloak_admin']
        config['services']['emqx']['admin_password'] = service_passwords['emqx_admin']
        config['services']['minio']['secret_key'] = service_passwords['minio_secret']
        config['services']['kong']['db_password'] = service_passwords['kong_db']
        
        # Validate volumes path
        volumes_path = config['system']['volumes_path']
        valid, message = setup_wizard.validate_volumes_path(volumes_path)
        if not valid:
            return jsonify({"error": f"Volumes path error: {message}"}), 400
        
        # Mark setup complete and save
        setup_wizard.complete_setup(config)
        
        return jsonify({"message": "Setup completed successfully"}), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Setup failed: {str(e)}"}), 500


# ==================== DASHBOARD ROUTES ====================

@app.route("/")
def dashboard():
    """Render main dashboard."""
    return render_template("dashboard.html")


@app.route("/api/status")
def get_status():
    """Get status of all services."""
    try:
        # Get master container status
        master = client.containers.get("supos-bedrock-master")
        master_status = master.status
        
        # Get service containers
        services = []
        
        # Postgres
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
        
        # EMQX
        try:
            emqx = client.containers.get("supos-emqx")
            services.append({
                "name": "emqx",
                "status": emqx.status,
                "health": "healthy" if emqx.status == "running" else "unhealthy"
            })
        except docker.errors.NotFound:
            services.append({
                "name": "emqx",
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
    """Start service stack using docker compose."""
    try:
        # Use docker-compose command
        os.system(f"cd /services && docker-compose up -d")
        return jsonify({"message": "Services starting"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/services/stop", methods=["POST"])
def stop_services():
    """Stop service stack."""
    try:
        os.system(f"cd /services && docker-compose down")
        return jsonify({"message": "Services stopped"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)