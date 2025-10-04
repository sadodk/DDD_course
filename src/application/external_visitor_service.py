from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import requests


@dataclass
class VisitorInfo:
    id: str
    type: str
    address: str
    city: str
    card_id: str
    email: str = ""
    # Add other fields as needed based on the API response


# For caching discuss with Domain how often the data changes
# Consider using a time-based cache invalidation strategy


class ExternalVisitorService:
    def __init__(self):
        self.base_url = "https://ddd-in-language.aardling.eu"
        self.headers = {
            "content-type": "application/json",
            "x-auth-token": "fZg124e-cuHb",
            "x-workshop-id": "DDD in Your Language - 2025 Sept-Oct",
        }
        self._users_cache: Optional[List[Dict[str, Any]]] = None

    def get_visitor_by_id(self, visitor_id: str) -> Optional[VisitorInfo]:
        """
        Get visitor information by ID from the external API.
        Returns None if visitor is not found.
        """
        users = self._get_all_users()

        for user in users:
            if user.id == visitor_id:
                return user

        return None

    def _get_all_users(self) -> List[VisitorInfo]:
        """
        Fetch all users from the external API.
        Uses caching to avoid multiple API calls.
        """
        if self._users_cache is None:
            try:
                response = requests.get(
                    f"{self.base_url}/api/users", headers=self.headers
                )
                response.raise_for_status()
                self._users_cache = response.json()
            except requests.RequestException as e:
                print(f"Error fetching users: {e}")
                self._users_cache = []

        return (
            []
            if self._users_cache is None
            else [VisitorInfo(**user) for user in self._users_cache]
        )

    def clear_cache(self) -> None:
        """Clear the users cache - useful for new scenarios."""
        self._users_cache = None


# Context class for scenario initialization
class Context:
    def __init__(self):
        self.external_visitor_service = ExternalVisitorService()

    def start_scenario(self) -> None:
        """Called at the start of each scenario to reset state."""
        self.external_visitor_service.clear_cache()
        # Visit tracking is now handled by VisitRepository in ApplicationContext
