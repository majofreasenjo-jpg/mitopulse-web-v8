import subprocess
import time
import os
import sys

# Define the full ecosystem map
SERVICES = {
    "gateway": {"dir": "gateway", "port": 8000},
    "presence_engine": {"dir": "presence_engine", "port": 8001},
    "risk_engine": {"dir": "risk_engine", "port": 8002},
    "continuity_engine": {"dir": "continuity_engine", "port": 8003},
    "trust_engine": {"dir": "trust_engine", "port": 8004},
    "fraud_memory": {"dir": "fraud_memory", "port": 8005},
    "graph_engine": {"dir": "graph_engine", "port": 8006},
    "policy_engine": {"dir": "policy_engine", "port": 8007},
    "device_trust_engine": {"dir": "device_trust_engine", "port": 8008},
    "anti_spoof_engine": {"dir": "anti_spoof_engine", "port": 8009},
    "dashboard": {"dir": "dashboard", "port": 8010},
    "feature_flag_service": {"dir": "feature_flag_service", "port": 8011},
    "challenge_engine": {"dir": "challenge_engine", "port": 8012},
    "admin_panel": {"dir": "admin_panel", "port": 8013},
    "reputation_network": {"dir": "reputation_network", "port": 8014},
    "identity_continuity_protocol": {"dir": "identity_continuity_protocol", "port": 8015},
    "edge_orchestrator": {"dir": "edge_orchestrator", "port": 8016},
}

# Define presentation profiles
PROFILES = {
    "1": {
        "name": "Básico (Inversores Generales / Visión Comercial)",
        "desc": "Gateway, Motores de Presencia y Riesgo, y el Dashboard. Prueba el concepto fundamental.",
        "services": ["gateway", "presence_engine", "risk_engine", "dashboard"]
    },
    "2": {
        "name": "Avanzado (VCs Técnicos / Director de Ciberseguridad)",
        "desc": "Agrega Memoria de Fraude, Continuidad de Identidad, Anti-Spoofing y Motores de Confianza.",
        "services": ["gateway", "presence_engine", "risk_engine", "dashboard", 
                     "trust_engine", "fraud_memory", "continuity_engine", "anti_spoof_engine", "admin_panel"]
    },
    "3": {
        "name": "Full Infraestructura Planetaria (Arquitectos de Sistemas / Due Diligence)",
        "desc": "Enciende los 16 microservicios. Red de Reputación, Grafos Globales, Edge Orchestrator.",
        "services": list(SERVICES.keys())
    }
}

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear()
    print("=========================================================")
    print("🚀 HUMA V4 - HUMAN INTERNET INFRASTRUCTURE LAUNCHER")
    print("=========================================================")
    print("\nSelecciona el nivel de complejidad ('Capas') a encender dependiendo de tu audiencia hoy:\n")
    
    for key, profile in PROFILES.items():
        print(f"[{key}] {profile['name']}")
        print(f"    └─ {profile['desc']}")
        print(f"    └─ Activa {len(profile['services'])} microservicios.\n")
    
    choice = input("Ingresa el número de perfil (1, 2 o 3): ")
    
    if choice not in PROFILES:
        print("Selección inválida. Saliendo...")
        sys.exit(1)
        
    selected_services = PROFILES[choice]["services"]
    
    # Base environment variables required by Huma v4 services to talk to each other
    env = os.environ.copy()
    env["PRESENCE_URL"] = "http://127.0.0.1:8001"
    env["RISK_URL"] = "http://127.0.0.1:8002"
    env["CONTINUITY_URL"] = "http://127.0.0.1:8003"
    env["TRUST_URL"] = "http://127.0.0.1:8004"
    env["FRAUD_URL"] = "http://127.0.0.1:8005"
    env["GRAPH_URL"] = "http://127.0.0.1:8006"
    env["POLICY_URL"] = "http://127.0.0.1:8007"
    env["DEVICE_TRUST_URL"] = "http://127.0.0.1:8008"
    env["ANTI_SPOOF_URL"] = "http://127.0.0.1:8009"
    env["FEATURE_FLAG_URL"] = "http://127.0.0.1:8011"
    env["CHALLENGE_URL"] = "http://127.0.0.1:8012"
    env["REPUTATION_URL"] = "http://127.0.0.1:8014"
    env["IDCP_URL"] = "http://127.0.0.1:8015"
    env["GATEWAY_URL"] = "http://127.0.0.1:8000"
    env["WEBHOOK_SECRET"] = "huma_v4_demo_secret"
    
    processes = []
    
    print(f"\n⚡ Iniciando Perfil: {PROFILES[choice]['name']}...")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Start the services
    for service_name in selected_services:
        svc_info = SERVICES[service_name]
        svc_dir = os.path.join(base_path, svc_info["dir"])
        port = svc_info["port"]
        
        if not os.path.isdir(svc_dir):
            print(f"  [X] ADVERTENCIA: Falta la carpeta '{svc_info['dir']}'. Se omitirá {service_name}.")
            continue
            
        print(f"  [+] Levantando {service_name} en el puerto {port}...")
        
        # Start uvicorn in a subprocess without showing full output to keep terminal clean
        # Using sys.executable to ensure we use the same Python interpreter
        cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)]
        
        # Open in a new window using powershell Start-Process so that we don't clog this terminal
        # OR just run them in background here. Running in new windows looks cooler for tech investors.
        window_title = f"[Huma v4] {service_name.upper()} (Port {port})"
        ps_cmd = f'Start-Process "{sys.executable}" -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port {port}" -WorkingDirectory "{svc_dir}" -WindowStyle Normal'
        
        try:
             subprocess.Popen(["powershell", "-Command", ps_cmd], env=env)
        except Exception as e:
             print(f"Error starting {service_name}: {e}")
             
        time.sleep(0.5) # Slight delay to let ports bind
        
    print("\n✅ Todos los microservicios seleccionados han sido enviados a ejecución.")
    print("\n🌐 RUTAS DE ACCESO:")
    if "dashboard" in selected_services:
        print("  - Dashboard Principal:   http://127.0.0.1:8010")
    if "admin_panel" in selected_services:
        print("  - Admin / Policy Panel:  http://127.0.0.1:8013")
    if "gateway" in selected_services:
        print("  - API Gateway Docs:      http://127.0.0.1:8000/docs")
        
    print("\nINFO: Cada servicio se abrió en una ventana de consola independiente.")
    print("Para apagarlos completamente, simplemente cierra todas esas ventanas negras de terminal emergentes.")
    print("Presiona Enter para salir de este lanzador...")
    input()

if __name__ == "__main__":
    main()
