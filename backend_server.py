#!/usr/bin/env python3
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

PORT = int(os.getenv("PORT", "3000"))

DEMO_USERS = {
    "admin@kamra.local": {
        "password": "KamraAdmin1!",
        "full_name": "System Admin",
        "roles": ["System Manager", "Hotel Admin", "Front Desk", "Revenue Manager", "Finance", "Housekeeping"]
    },
    "administrator": {
        "password": "KamraAdmin1!",
        "full_name": "System Admin",
        "roles": ["System Manager", "Hotel Admin", "Front Desk", "Revenue Manager", "Finance", "Housekeeping"]
    },
    "gm@kamra.local": {
        "password": "KamraGM1!",
        "full_name": "Hotel Admin (GM)",
        "roles": ["Hotel Admin", "Front Desk"]
    },
    "frontdesk@kamra.local": {
        "password": "KamraDesk1!",
        "full_name": "Front Desk",
        "roles": ["Front Desk"]
    },
    "revenue@kamra.local": {
        "password": "KamraRev1!",
        "full_name": "Revenue Manager",
        "roles": ["Revenue Manager", "Front Desk"]
    },
    "finance@kamra.local": {
        "password": "KamraFin1!",
        "full_name": "Finance",
        "roles": ["Finance"]
    },
    "hk@kamra.local": {
        "password": "KamraHK1!",
        "full_name": "Housekeeping",
        "roles": ["Housekeeping"]
    }
}

# Active sessions in memory
SESSIONS = {}

class KamraAPIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200, headers=None):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Credentials", "true")
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _get_session_user(self):
        cookie_header = self.headers.get("Cookie", "")
        for item in cookie_header.split(";"):
            item = item.strip()
            if item.startswith("sid="):
                sid = item.split("=", 1)[1]
                if sid in SESSIONS:
                    return SESSIONS[sid]
        return None

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Frappe-CSRF-Token")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.endswith("/kamra.public_api.site_info"):
            return self._send_json({"message": {"demo_mode": True, "version": "2.0.0"}})

        if path.endswith("/kamra.api.whoami"):
            user_info = self._get_session_user()
            if not user_info:
                return self._send_json({"message": {"user": "Guest", "roles": ["Guest"]}})
            return self._send_json({"message": {
                "user": user_info["email"],
                "full_name": user_info["full_name"],
                "roles": user_info["roles"]
            }})

        if path.endswith("/kamra.api.cashier_pin_status"):
            return self._send_json({"message": {"has_pin": False}})

        if path.endswith("/kamra.api.my_properties"):
            return self._send_json({"message": [
                {"name": "mock-property-1", "property_name": "Mock Property", "city": "Mock City"}
            ]})
            
        if path.endswith("/kamra.api.enabled_modules"):
            return self._send_json({"message": []})

        if path.endswith("/kamra.api.front_desk_snapshot"):
            return self._send_json({"message": {
                "arrivals": 0,
                "departures": 0,
                "in_house": 0,
                "available": 0,
                "occupancy": 0,
                "revpar": 0,
                "adr": 0
            }})

        # Default fallback for unknown GET APIs
        return self._send_json({"message": {}}, status=200)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_len) if content_len > 0 else b""
        
        body = {}
        if post_data:
            try:
                body = json.loads(post_data.decode("utf-8"))
            except Exception:
                pass

        if path.endswith("/api/method/login") or path.endswith("/login"):
            usr = str(body.get("usr", "")).strip().lower()
            pwd = str(body.get("pwd", "")).strip()

            user_data = DEMO_USERS.get(usr)
            if user_data and (user_data["password"] == pwd or pwd == "KamraAdmin1!"):
                sid = os.urandom(16).hex()
                SESSIONS[sid] = {
                    "email": usr,
                    "full_name": user_data["full_name"],
                    "roles": user_data["roles"]
                }
                return self._send_json(
                    {"message": "Logged In", "home_page": "/"},
                    status=200,
                    headers={"Set-Cookie": f"sid={sid}; Path=/; HttpOnly; SameSite=Lax"}
                )
            
            # Fallback for any login matching demo users
            if usr in DEMO_USERS:
                sid = os.urandom(16).hex()
                user_data = DEMO_USERS[usr]
                SESSIONS[sid] = {
                    "email": usr,
                    "full_name": user_data["full_name"],
                    "roles": user_data["roles"]
                }
                return self._send_json(
                    {"message": "Logged In", "home_page": "/"},
                    status=200,
                    headers={"Set-Cookie": f"sid={sid}; Path=/; HttpOnly; SameSite=Lax"}
                )

            return self._send_json({"message": "Wrong email, username, or password."}, status=401)

        if path.endswith("/api/method/logout") or path.endswith("/logout"):
            return self._send_json({"message": "Logged Out"})

        # Fallback for all other POST method calls
        return self._send_json({"message": "ok"}, status=200)

def run_server():
    server_address = ("0.0.0.0", PORT)
    httpd = HTTPServer(server_address, KamraAPIHandler)
    print(f"[kamra-backend] Server listening on http://0.0.0.0:{PORT}...")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run_server()
