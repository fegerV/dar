"""Locust load testing configuration for DarAgent API."""

from locust import HttpUser, between, task


class AnonymousUser(HttpUser):
    """Simulate anonymous users hitting public endpoints."""

    wait_time = between(1, 3)
    weight = 3

    @task(5)
    def health_check(self):
        """Test health endpoint."""
        self.client.get("/health")

    @task(3)
    def list_templates(self):
        """Test templates listing."""
        self.client.get("/api/v1/templates")

    @task(2)
    def get_template_detail(self):
        """Test template detail."""
        self.client.get("/api/v1/templates/some-template-id")

    @task(1)
    def get_stats(self):
        """Test public stats."""
        self.client.get("/api/v1/stats")


class AuthenticatedUser(HttpUser):
    """Simulate authenticated users performing actions."""

    wait_time = between(2, 5)
    weight = 2

    def on_start(self):
        """Login and get token."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "loadtest@example.com",
                "password": "LoadTestPass123!",
            },
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
        else:
            self.token = None

    @task(3)
    def get_user_profile(self):
        """Test user profile endpoint."""
        if self.token:
            self.client.get(
                "/api/v1/users/me",
                headers={"Authorization": f"Bearer {self.token}"},
            )

    @task(2)
    def list_people(self):
        """Test people listing."""
        if self.token:
            self.client.get(
                "/api/v1/people",
                headers={"Authorization": f"Bearer {self.token}"},
            )

    @task(2)
    def send_chat_message(self):
        """Test chat message endpoint."""
        if self.token:
            self.client.post(
                "/api/v1/chat/message",
                json={"text": "Привет! Хочу поздравить маму"},
                headers={"Authorization": f"Bearer {self.token}"},
            )

    @task(1)
    def create_person(self):
        """Test person creation."""
        if self.token:
            self.client.post(
                "/api/v1/people",
                json={
                    "name": "Тест",
                    "relationship": "parent",
                },
                headers={"Authorization": f"Bearer {self.token}"},
            )


class AdminUser(HttpUser):
    """Simulate admin users performing admin operations."""

    wait_time = between(3, 7)
    weight = 1

    def on_start(self):
        """Login as admin."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@test.com",
                "password": "AdminPass123!",
            },
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
        else:
            self.token = None

    @task(3)
    def get_dashboard_stats(self):
        """Test admin dashboard stats."""
        if self.token:
            self.client.get(
                "/admin/stats",
                headers={"Authorization": f"Bearer {self.token}"},
            )

    @task(2)
    def list_users(self):
        """Test user listing."""
        if self.token:
            self.client.get(
                "/admin/users?page=1&page_size=20",
                headers={"Authorization": f"Bearer {self.token}"},
            )

    @task(2)
    def list_generations(self):
        """Test generation listing."""
        if self.token:
            self.client.get(
                "/admin/generations?page=1&page_size=20",
                headers={"Authorization": f"Bearer {self.token}"},
            )

    @task(1)
    def list_queue(self):
        """Test queue listing."""
        if self.token:
            self.client.get(
                "/admin/queue",
                headers={"Authorization": f"Bearer {self.token}"},
            )

    @task(1)
    def ai_health_check(self):
        """Test AI health check endpoint."""
        if self.token:
            self.client.get(
                "/admin/ai/health",
                headers={"Authorization": f"Bearer {self.token}"},
            )


class GenerationLoadUser(HttpUser):
    """Simulate heavy generation load."""

    wait_time = between(5, 10)
    weight = 1

    def on_start(self):
        """Login and setup."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "loadtest@example.com",
                "password": "LoadTestPass123!",
            },
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
        else:
            self.token = None

    @task(1)
    def create_generation(self):
        """Test generation creation."""
        if self.token:
            self.client.post(
                "/api/v1/generations",
                json={
                    "project_id": "test-project-id",
                    "template_version_id": "test-template-version-id",
                },
                headers={"Authorization": f"Bearer {self.token}"},
            )

    @task(3)
    def check_generation_status(self):
        """Test generation status polling."""
        if self.token:
            self.client.get(
                "/api/v1/generations/test-generation-id",
                headers={"Authorization": f"Bearer {self.token}"},
            )
