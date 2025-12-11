#!/usr/bin/env python3
"""
OAuth 2.0 Authentication Demo
Demonstrates OAuth login flow integration with the existing system
"""

import http.server
import socketserver
import threading
import time
import webbrowser
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests

# Configuration
BASE_URL = "http://localhost:8000"
CALLBACK_PORT = 3001
CALLBACK_URL = f"http://localhost:{CALLBACK_PORT}"


class OAuthDemo:
    def __init__(self):
        self.access_token = None
        self.user_info = None
        self.callback_server = None

    def start_callback_server(self):
        """Start local server to handle OAuth callback"""

        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def __init__(self, demo_instance):
                self.demo = demo_instance

            def __call__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def do_GET(self):
                # Parse callback URL
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)

                if "access_token" in params:
                    # OAuth success with token in URL
                    self.demo.access_token = params["access_token"][0]
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(
                        b"""
                    <html>
                        <body>
                            <h2>OAuth Login Successful!</h2>
                            <p>You can close this window and return to the terminal.</p>
                        </body>
                    </html>
                    """
                    )
                elif "code" in params and "state" in params:
                    # OAuth callback with code (would need backend processing)
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(
                        b"""
                    <html>
                        <body>
                            <h2>OAuth Callback Received</h2>
                            <p>Processing authentication...</p>
                            <script>
                                // In a real app, send code to backend
                                setTimeout(() => {
                                    window.close();
                                }, 2000);
                            </script>
                        </body>
                    </html>
                    """
                    )
                else:
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"OAuth callback error")

            def log_message(self, format, *args):
                pass  # Suppress server logs

        handler = CallbackHandler(self)
        self.callback_server = socketserver.TCPServer(("", CALLBACK_PORT), handler)

        # Start server in background thread
        server_thread = threading.Thread(target=self.callback_server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print(f"Started callback server on {CALLBACK_URL}")

    def stop_callback_server(self):
        """Stop the callback server"""
        if self.callback_server:
            self.callback_server.shutdown()
            self.callback_server.server_close()

    def get_oauth_providers(self) -> dict[str, Any]:
        """Get available OAuth providers"""
        try:
            response = requests.get(f"{BASE_URL}/auth/oauth/providers")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get OAuth providers: {e}")
            return {"providers": []}

    def initiate_oauth_login(self, provider: str) -> bool:
        """Initiate OAuth login flow"""
        try:
            # Start callback server
            self.start_callback_server()

            # Construct OAuth login URL with callback
            login_url = f"{BASE_URL}/auth/oauth/{provider}/login"
            login_url += f"?redirect_url={CALLBACK_URL}"

            print(f"Opening OAuth login for {provider}...")
            print(f"If browser doesn't open, visit: {login_url}")

            # Open browser for OAuth login
            webbrowser.open(login_url)

            # Wait for callback (timeout after 60 seconds)
            print("Waiting for OAuth callback...")
            timeout = 60
            while timeout > 0 and not self.access_token:
                time.sleep(1)
                timeout -= 1

            self.stop_callback_server()

            if self.access_token:
                print("✅ OAuth login successful!")
                return True
            print("❌ OAuth login timed out or failed")
            return False

        except Exception as e:
            print(f"OAuth login error: {e}")
            self.stop_callback_server()
            return False

    def get_user_profile(self) -> dict[str, Any]:
        """Get user profile using access token"""
        if not self.access_token:
            print("No access token available")
            return {}

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{BASE_URL}/auth/secure-agent", headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get user profile: {e}")
            return {}

    def get_oauth_accounts(self) -> dict[str, Any]:
        """Get linked OAuth accounts"""
        if not self.access_token:
            print("No access token available")
            return {}

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{BASE_URL}/auth/oauth/accounts", headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get OAuth accounts: {e}")
            return {}

    def test_api_access(self) -> bool:
        """Test API access with OAuth token"""
        if not self.access_token:
            print("No access token available")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}

            # Test existing secure endpoint
            response = requests.get(f"{BASE_URL}/auth/secure-agent", headers=headers)
            response.raise_for_status()

            print("✅ API access successful with OAuth token")
            print(f"Response: {response.json()}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ API access failed: {e}")
            return False


def main():
    """Main demo function"""
    print("🔐 OAuth 2.0 Authentication Demo")
    print("=" * 40)

    demo = OAuthDemo()

    try:
        # 1. Get available OAuth providers
        print("\n1. Getting available OAuth providers...")
        providers_response = demo.get_oauth_providers()
        providers = providers_response.get("providers", [])

        if not providers:
            print("❌ No OAuth providers available")
            print("Make sure the server is running and OAuth is configured")
            return

        print("📋 Available providers:")
        for i, provider in enumerate(providers, 1):
            print(f"   {i}. {provider['display_name']} ({provider['name']})")

        # 2. Choose provider
        print("\n2. Choose OAuth provider:")
        try:
            choice = int(input(f"Enter choice (1-{len(providers)}): "))
            if 1 <= choice <= len(providers):
                selected_provider = providers[choice - 1]["name"]
            else:
                print("Invalid choice")
                return
        except ValueError:
            print("Invalid input")
            return

        # 3. Initiate OAuth login
        print(f"\n3. Initiating {selected_provider.title()} OAuth login...")
        success = demo.initiate_oauth_login(selected_provider)

        if not success:
            print("OAuth login failed")
            return

        # 4. Test API access
        print("\n4. Testing API access with OAuth token...")
        demo.test_api_access()

        # 5. Get OAuth accounts
        print("\n5. Getting linked OAuth accounts...")
        accounts = demo.get_oauth_accounts()
        if accounts:
            print("🔗 Linked OAuth accounts:")
            for account in accounts.get("oauth_accounts", []):
                print(f"   - {account['provider'].title()}: {account['provider_username']}")

        # 6. Demo additional features
        print("\n6. Additional features available:")
        print("   - Link additional OAuth accounts: POST /auth/oauth/{provider}/link")
        print("   - Unlink OAuth accounts: DELETE /auth/oauth/{provider}/unlink")
        print("   - Use OAuth token for all API endpoints")

        print("\n✅ OAuth demo completed successfully!")
        print(f"\n💡 Your access token: {demo.access_token[:20]}...")
        print("   You can now use this token for API calls")

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    finally:
        demo.stop_callback_server()


if __name__ == "__main__":
    print("🚀 Starting OAuth Demo...")
    print("\nPrerequisites:")
    print("1. FastAPI server running on http://localhost:8000")
    print("2. OAuth providers configured (Google/GitHub)")
    print("3. Internet connection for OAuth flow")

    input("\nPress Enter to continue...")

    main()
