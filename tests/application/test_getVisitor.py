from application.external_visitor_service import ExternalVisitorService


def test_get_visitor_by_id_integration():
    """Test the visitor service against the real API."""
    # Arrange
    service = ExternalVisitorService()

    # Act - Try to get all users first to see what's available
    users = service._get_all_users()
    print(f"Found {len(users)} users from API")

    if users:
        # Test with the first user's ID
        first_user_id = users[0].id
        visitor = service.get_visitor_by_id(first_user_id)

        # Assert
        assert visitor is not None
        assert visitor.id == first_user_id
        print(f"Successfully found visitor: {visitor.city}")

        # Test with non-existent ID
        non_existent_visitor = service.get_visitor_by_id("non-existent-id")
        assert non_existent_visitor is None
        print("Correctly returned None for non-existent visitor")
    else:
        print("No users found in API response")
