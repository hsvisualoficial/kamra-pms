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

    def _handle_api_request(self, path, body=None):
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
            import datetime
            return self._send_json({"message": {
                "date": datetime.date.today().isoformat(),
                "arrivals": [],
                "departures": [],
                "in_house": [],
                "rooms": [],
                "minutes_saved_30d": 0
            }})

        if path.endswith("/kamra.api.availability_calendar") or path.endswith("/kamra.api.venue_calendar"):
            return self._send_json({"message": {
                "start": "2026-09-17",
                "days": 14,
                "dates": [],
                "room_types": [],
                "venues": []
            }})

        if path.endswith("/kamra.api.tape_chart") or path.endswith("/kamra.api.tape_chart_hourly"):
            return self._send_json({"message": {
                "start": "2026-09-17",
                "days": 14,
                "dates": [],
                "rooms": [],
                "unassigned": []
            }})

        if path.endswith("/kamra.dashboards.property_dashboard"):
            import datetime
            return self._send_json({"message": {
                "property_name": "Mock Property",
                "date": datetime.date.today().isoformat(),
                "total_rooms": 0,
                "occupancy_pct": 0,
                "arrivals": 0,
                "departures": 0,
                "in_house": 0,
                "no_shows": 0,
                "revenue_today": 0,
                "collections_today": 0,
                "statistics": {
                    "mtd_occupancy_pct": 0,
                    "mtd_revenue": 0,
                    "adr": 0,
                    "revpar": 0,
                    "rooms_sold_mtd": 0
                },
                "housekeeping": {
                    "room_status": {},
                    "occupied": 0,
                    "vacant": 0,
                    "open_tasks": 0,
                    "overdue_tasks": 0
                },
                "finance": {
                    "collections_today": 0,
                    "outstanding": 0,
                    "open_folios": 0
                }
            }})

        if path.endswith("/kamra.dashboards.portfolio_dashboard"):
            import datetime
            return self._send_json({"message": {
                "date": datetime.date.today().isoformat(),
                "totals": {
                    "properties": 1,
                    "total_rooms": 0,
                    "occupancy_pct": 0,
                    "arrivals": 0,
                    "departures": 0,
                    "in_house": 0,
                    "revenue_today": 0,
                    "collections_today": 0,
                    "outstanding": 0
                },
                "properties": []
            }})
        if path.endswith("/kamra.reports.budget_vs_actual"):
            return self._send_json({"message": {
                "period": "2026-09",
                "days_elapsed": 1,
                "total_days": 30,
                "rows": [],
                "has_budget": False
            }})

        if path.endswith("/kamra.reports.contribution"):
            return self._send_json({"message": {
                "by": "",
                "total": 0,
                "rows": []
            }})

        if path.endswith("/kamra.cashier.list_sessions"):
            return self._send_json({"message": {
                "sessions": [],
                "business_date": "2026-09-17"
            }})

        if path.endswith("/kamra.reports.sla_report"):
            return self._send_json({"message": {
                "from": "",
                "to": "",
                "total": 0,
                "resolved": 0,
                "open": 0,
                "breached": 0,
                "breach_pct": 0,
                "avg_resolve_mins": 0,
                "by_category": [],
                "by_priority": [],
                "overdue": []
            }})

        if path.endswith("/kamra.banquet.banquet_pipeline"):
            return self._send_json({"message": {
                "from": "",
                "to": "",
                "months": [],
                "by_status": [],
                "by_event_type": [],
                "by_venue": [],
                "by_source": [],
                "totals": {
                    "functions": 0,
                    "confirmed_value": 0,
                    "pipeline_value": 0,
                    "outstanding": 0,
                    "conversion_rate": 0
                },
                "lost_reasons": []
            }})

        if path.endswith("/kamra.banquet.banquet_reminders"):
            return self._send_json({"message": {
                "count": 0,
                "functions": []
            }})

        if path.endswith("/kamra.banquet.banquet_catalogue"):
            return self._send_json({"message": {
                "menus": [], "services": [], "venues": []
            }})

        if path.endswith("/kamra.banquet.banquet_register"):
            return self._send_json({"message": {
                "register": "", "title": "", "from": "", "to": "", "rows": [], "totals": { "count": 0, "value": 0 }
            }})

        if path.endswith("/kamra.banquet.month_availability"):
            return self._send_json({"message": {
                "month": "", "start": "", "end": "", "dates": [], "utilisation": 0, "venues": [], "rows": []
            }})

        if path.endswith("/kamra.api.fx_rates"):
            return self._send_json({"message": {
                "rates": {}
            }})

        if path.endswith("/kamra.api.fx_transactions"):
            return self._send_json({"message": {
                "transactions": []
            }})

        if path.endswith("/kamra.folio.history"):
            return self._send_json({"message": {
                "folios": []
            }})

        if path.endswith("/kamra.accounting.export_invoices"):
            return self._send_json({"message": {
                "rows": [], "components": [], "tax_label": "", "tax_id_label": "", "currency": "", "totals": { "invoices": 0, "taxable": 0, "total_tax": 0, "grand_total": 0 }
            }})

        if path.endswith("/kamra.health.system_health"):
            return self._send_json({"message": {
                "overall": "ok",
                "summary": { "ok": 1, "warn": 0, "fail": 0 },
                "installed": { "kamra": "mock", "frappe": "mock", "site": "mock" },
                "latest": { "ok": True, "tag": "", "name": "", "url": "", "published_at": "" }
            }})

        if path.endswith("/kamra.reports.manager_flash"):
            return self._send_json({"message": {
                "date": "", "total_rooms": 0, "today": None, "mtd": { "occupancy_pct": 0, "date": "", "rooms_sold": 0, "pax": 0, "room_revenue": 0, "fnb_revenue": 0, "other_revenue": 0, "total_revenue": 0 }, "movement": { "arrivals": 0, "departures": 0, "in_house": 0, "no_shows": 0 }, "collections": { "modes": [], "grand_total": 0 }, "trend": [], "outlook": []
            }})

        return None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        handled = self._handle_api_request(path)
        if handled is not None:
            return

        if path.startswith("/api/resource/"):
            return self._send_json({"data": []}, status=200)

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

        handled = self._handle_api_request(path, body)
        if handled is not None:
            return

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

        # Fallback for all other POST method calls (returns an empty array so .map() doesn't crash)
        return self._send_json({"message": []}, status=200)

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
