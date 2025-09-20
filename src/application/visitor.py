from application.external_visitor_repository import Context

# In your application code
context = Context()
visitor_service = context.external_visitor_service

# Get a specific visitor
visitor = visitor_service.get_visitor_by_id("some-visitor-id")
if visitor:
    print(f"Found visitor: {visitor.city}")
else:
    print("Visitor not found")
