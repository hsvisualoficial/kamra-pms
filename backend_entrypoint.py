import os
import json

def setup_frappe_env():
    sites_dir = os.path.abspath("sites")
    os.makedirs(sites_dir, exist_ok=True)

    site_name = os.getenv("FRAPPE_SITE", "kamra.localhost")
    site_dir = os.path.join(sites_dir, site_name)
    os.makedirs(site_dir, exist_ok=True)

    db_host = os.getenv("DB_HOST", "pms-db")
    try:
        db_port = int(os.getenv("DB_PORT", "3306"))
    except ValueError:
        db_port = 3306

    db_name = os.getenv("DB_NAME", "kamra")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")

    common_config = {
        "db_host": db_host,
        "db_port": db_port,
        "db_type": "mariadb",
    }
    with open(os.path.join(sites_dir, "common_site_config.json"), "w") as f:
        json.dump(common_config, f, indent=2)

    site_config = {
        "db_name": db_name,
        "db_user": db_user,
        "db_password": db_password,
        "db_type": "mariadb",
        "encryption_key": "kamra_secret_key_12345"
    }
    with open(os.path.join(site_dir, "site_config.json"), "w") as f:
        json.dump(site_config, f, indent=2)

    with open(os.path.join(sites_dir, "current_site.txt"), "w") as f:
        f.write(site_name)

    print(f"[kamra-backend] Initialized Frappe site configuration for '{site_name}' (db: {db_host}:{db_port})")

if __name__ == "__main__":
    setup_frappe_env()
