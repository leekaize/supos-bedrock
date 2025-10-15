import docker
from flask import Flask, render_template, jsonify, request, redirect, url_for, Response
import os
import subprocess
import setup_wizard

app = Flask(__name__)
client = docker.from_env()

SUPOS_CE_PATH = "/supos-ce"
SUPOS_CE_COMPOSE = "docker-compose-4c8g.yml"


# ==================== STARTUP ====================

def initialize_environment():
    """Generate .env on startup if configured."""
    if not setup_wizard.is_first_run():
        config = setup_wizard.load_config()
        success, message = setup_wizard.generate_env_file(config)
        if success:
            print(f"✓ {message}")
        else:
            print(f"⚠ {message}")

initialize_environment()


# ==================== MIDDLEWARE ====================

@app.before_request
def check_first_run():
    """Redirect to setup if not configured."""
    if setup_wizard.is_first_run():
        if request.path.startswith('/setup') or request.path.startswith('/api/setup'):
            return None
        return redirect(url_for('setup_page'))


# ==================== SETUP ====================

@app.route("/setup")
def setup_page():
    """First-run wizard."""
    if not setup_wizard.is_first_run():
        return redirect(url_for('dashboard'))
    return render_template("setup.html")


@app.route("/api/setup/validate", methods=["POST"])
def validate_setup():
    """System requirements check."""
    try:
        valid, issues, warnings = setup_wizard.validate_system_requirements()
        return jsonify({"valid": valid, "issues": issues, "warnings": warnings}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/setup/complete", methods=["POST"])
def complete_setup():
    """Save configuration."""
    try:
        data = request.get_json()
        config = setup_wizard.load_config()
        
        # Admin user
        admin_data = data.get('admin', {})
        config['admin'] = setup_wizard.create_admin_user(
            username=admin_data.get('username'),
            email=admin_data.get('email'),
            password=admin_data.get('password')
        )
        
        # Network
        network_data = data.get('network', {})
        config['network']['domain'] = network_data.get('domain')
        config['network']['port'] = network_data.get('port')
        config['localization']['language'] = data.get('language', 'en-US')
        
        # Service passwords
        passwords = setup_wizard.generate_service_passwords()
        config['services']['postgres']['password'] = passwords['postgres']
        config['services']['keycloak']['admin_password'] = passwords['keycloak_admin']
        config['services']['emqx']['admin_password'] = passwords['emqx_admin']
        config['services']['minio']['secret_key'] = passwords['minio_secret']
        config['services']['kong']['db_password'] = passwords['kong_db']
        
        # Validate volumes path
        valid, message = setup_wizard.validate_volumes_path(config['system']['volumes_path'])
        if not valid:
            return jsonify({"error": f"Path error: {message}"}), 400
        
        setup_wizard.complete_setup(config)
        
        # Generate .env
        success, msg = setup_wizard.generate_env_file(config)
        if not success:
            print(f"⚠ {msg}")
        
        return jsonify({"message": "Setup complete"}), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== DASHBOARD ====================

@app.route("/")
def dashboard():
    """Main UI."""
    return render_template("dashboard.html")


# ==================== SUPOS-CE ====================

@app.route("/api/supos/status")
def supos_status():
    """Check supOS-CE state."""
    compose_path = f"{SUPOS_CE_PATH}/{SUPOS_CE_COMPOSE}"
    
    if not os.path.exists(compose_path):
        return jsonify({
            "installed": False,
            "configured": False,
            "message": "Submodule not mounted or missing"
        }), 200
    
    # Count containers - this is the TRUE indicator
    try:
        all_containers = []
        for name in ["frontend", "backend", "keycloak", "postgresql", "emqx", "tsdb", "nodered", "kong"]:
            all_containers.extend(client.containers.list(all=True, filters={"name": name}))
        
        running = [c for c in all_containers if c.status == "running"]
        
        # Configured = services were started (containers exist)
        configured = len(all_containers) > 0
        
        return jsonify({
            "installed": True,
            "configured": configured,
            "running": len(running) > 0,
            "container_count": len(all_containers),
            "running_count": len(running)
        }), 200
    except Exception as e:
        return jsonify({
            "installed": True,
            "configured": False,
            "running": False,
            "error": str(e)
        }), 200


@app.route("/api/supos/install", methods=["GET"])
def install_supos():
    """Configure and start supOS-CE."""
    
    def generate():
        try:
            compose_path = f"{SUPOS_CE_PATH}/{SUPOS_CE_COMPOSE}"
            
            if not os.path.exists(compose_path):
                yield f'data: {{"type": "error", "message": "Submodule not found. Check mount."}}\n\n'
                return
            
            yield f'data: {{"type": "info", "message": "Configuring supOS-CE..."}}\n\n'
            
            # Load config
            config = setup_wizard.load_config()
            volumes_base = config['system']['volumes_path']
            
            # Create required volume directories
            yield f'data: {{"type": "info", "message": "Creating volume directories..."}}\n\n'
            
            required_dirs = [
                'postgresql/pgdata', 'postgresql/conf', 'postgresql/init-scripts',
                'tsdb/data', 'tsdb/conf', 'tsdb/init-scripts',
                'emqx/data', 'emqx/log', 'emqx/config',
                'keycloak/data', 'keycloak/theme/keycloak.v2',
                'node-red', 'eventflow',
                'kong', 'konga/db',
                'backend/apps', 'backend/third-apps', 'backend/uns', 'backend/system', 'backend/log',
                'portainer', 'chat2db/data'
            ]
            
            for dir_path in required_dirs:
                full_path = os.path.join(volumes_base, dir_path)
                os.makedirs(full_path, exist_ok=True)
            
            yield f'data: {{"type": "success", "message": "Volume directories created"}}\n\n'
            
            # Generate .env
            yield f'data: {{"type": "info", "message": "Generating .env..."}}\n\n'
            
            success, msg = setup_wizard.generate_env_file(
                config,
                template_path='/services/.env.template',
                output_path=f'{SUPOS_CE_PATH}/.env'
            )
            
            if not success:
                yield f'data: {{"type": "error", "message": "Env generation failed: {msg}"}}\n\n'
                return
            
            yield f'data: {{"type": "success", "message": "Configuration ready"}}\n\n'
            
            # Start services
            yield f'data: {{"type": "info", "message": "Starting services..."}}\n\n'
            
            process = subprocess.Popen(
                ["docker-compose", "-f", SUPOS_CE_COMPOSE, "up", "-d"],
                cwd=SUPOS_CE_PATH,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    clean = line.strip().replace('"', '\\"').replace('\n', '')
                    yield f'data: {{"type": "log", "message": "{clean}"}}\n\n'
            
            process.wait()
            
            if process.returncode == 0:
                yield f'data: {{"type": "success", "message": "Services started"}}\n\n'
                yield f'data: {{"type": "complete"}}\n\n'
            else:
                yield f'data: {{"type": "error", "message": "Startup failed code {process.returncode}"}}\n\n'
                
        except Exception as e:
            yield f'data: {{"type": "error", "message": "Error: {str(e)}"}}\n\n'
    
    return Response(generate(), mimetype='text/event-stream')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)