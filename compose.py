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
    res = subprocess.run(
        ["npx", "@apollo/rover", "supergraph", "compose", "--config", yaml_path],
        cwd=base_dir,
        capture_output=True,
        text=True,
        shell=True
    )
    if res.returncode != 0:
        print("Error composing supergraph:", res.stderr)
        sys.exit(1)
        
    supergraph_path = os.path.join(base_dir, "supergraph.graphql")
    with open(supergraph_path, "w", encoding="utf-8") as f:
        f.write(res.stdout)
    print(f"Saved: {supergraph_path}")
    print("\n[+] Supergraph composed successfully!")

if __name__ == "__main__":
    main()
