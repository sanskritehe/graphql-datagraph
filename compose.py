import os
import subprocess
import sys

def export_schema_to_file(service_dir, output_file):
    # Dynamically import the app.graphql_schema or app.graphql.schema and call schema.as_str()
    sys.path.insert(0, service_dir)
    try:
        try:
            from app.graphql.schema import schema
        except ImportError:
            from app.graphql_schema import schema
        schema_str = schema.as_str()
    except Exception as e:
        print(f"Error importing schema from {service_dir}: {e}")
        sys.exit(1)
    finally:
        # Clean up path to prevent overlap
        if service_dir in sys.path:
            sys.path.remove(service_dir)
        # Unload app modules from sys.modules to prevent cross-import pollution
        for mod in list(sys.modules.keys()):
            if mod == "app" or mod.startswith("app."):
                del sys.modules[mod]
                
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(schema_str)
    print(f"Saved: {output_file}")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    appointment_service_dir = os.path.abspath(os.path.join(base_dir, "..", "Appointment-Service"))
    appointment_db_service_dir = os.path.abspath(os.path.join(base_dir, "..", "Appointment-Database-Service"))
    
    print("--- 1. Exporting Appointment-Service Schema ---")
    export_schema_to_file(appointment_service_dir, os.path.join(base_dir, "appointment-service.graphql"))
    
    print("\n--- 2. Exporting Appointment-Database-Service Schema ---")
    export_schema_to_file(appointment_db_service_dir, os.path.join(base_dir, "appointment-db-service.graphql"))
    
    print("\n--- 3. Composing Supergraph Schema ---")
    yaml_path = os.path.join(base_dir, "supergraph.yaml")
    
    stdout_data = None
    try_wsl = False
    
    try:
        res = subprocess.run(
            ["npx", "@apollo/rover", "supergraph", "compose", "--config", yaml_path],
            cwd=base_dir,
            capture_output=True,
            text=True,
            shell=True
        )
        if res.returncode != 0:
            err_msg = res.stderr or ""
            if "blocked" in err_msg.lower() or "spawn" in err_msg or "unknown" in err_msg.lower() or res.returncode == 1:
                try_wsl = True
            else:
                print("Error composing supergraph natively:", res.stderr)
                sys.exit(1)
        else:
            stdout_data = res.stdout
    except Exception as e:
        print(f"Native composition failed with exception: {e}")
        try_wsl = True

    if try_wsl:
        print("[!] Native Rover execution failed or blocked by policy. Falling back to WSL...")
        wsl_path = base_dir.replace("\\", "/")
        if ":" in wsl_path:
            drive, path = wsl_path.split(":", 1)
            wsl_path = f"/mnt/{drive.lower()}{path}"
        
        wsl_cmd = (
            f"wsl -d Ubuntu sh -c "
            f"\"export APOLLO_ELV2_LICENSE=accept && "
            f"cd {wsl_path} && "
            f"~/.rover/bin/rover supergraph compose --config ./supergraph.yaml\""
        )
        res_wsl = subprocess.run(
            wsl_cmd,
            capture_output=True,
            text=True,
            shell=True
        )
        if res_wsl.returncode != 0:
            print("Error composing supergraph via WSL:", res_wsl.stderr)
            sys.exit(1)
        stdout_data = res_wsl.stdout
        
    supergraph_path = os.path.join(base_dir, "supergraph.graphql")
    with open(supergraph_path, "w", encoding="utf-8") as f:
        f.write(stdout_data)
    print(f"Saved: {supergraph_path}")
    print("\n[+] Supergraph composed successfully!")

if __name__ == "__main__":
    main()
