from domain.services.monthly_visit_tracker_service import MonthlyVisitTracker
from domain.values.price import Price, Currency


class TestMonthlyVisitTracker:
    def test_single_visit_no_surcharge(self):
        """Test that the first visit in a month has no surcharge."""
        tracker = MonthlyVisitTracker()

        # Record first visit
        tracker.record_visit("user1", "2025-09-15T10:00:00Z", "visit1")

        # Check visit count and surcharge
        count = tracker.get_monthly_visit_count("user1", "2025-09-15T10:00:00Z")
        should_apply = tracker.should_apply_surcharge("user1", "2025-09-15T10:00:00Z")

        assert count == 1
        assert should_apply is False

    def test_second_visit_no_surcharge(self):
        """Test that the second visit in a month has no surcharge."""
        tracker = MonthlyVisitTracker()

        # Record two visits in same month
        tracker.record_visit("user1", "2025-09-15T10:00:00Z", "visit1")
        tracker.record_visit("user1", "2025-09-20T10:00:00Z", "visit2")

        # Check visit count and surcharge
        count = tracker.get_monthly_visit_count("user1", "2025-09-20T10:00:00Z")
        should_apply = tracker.should_apply_surcharge("user1", "2025-09-20T10:00:00Z")

        assert count == 2
        assert should_apply is False

    def test_third_visit_applies_surcharge(self):
        """Test that the third visit in a month applies 5% surcharge."""
        tracker = MonthlyVisitTracker()

        # Record three visits in same month
        tracker.record_visit("user1", "2025-09-15T10:00:00Z", "visit1")
        tracker.record_visit("user1", "2025-09-20T10:00:00Z", "visit2")
        tracker.record_visit("user1", "2025-09-25T10:00:00Z", "visit3")

        # Check visit count and surcharge
        count = tracker.get_monthly_visit_count("user1", "2025-09-25T10:00:00Z")
        should_apply = tracker.should_apply_surcharge("user1", "2025-09-25T10:00:00Z")

        assert count == 3
        assert should_apply is True

    def test_fourth_visit_also_applies_surcharge(self):
        """Test that the fourth and subsequent visits also apply surcharge."""
        tracker = MonthlyVisitTracker()

        # Record four visits in same month
        tracker.record_visit("user1", "2025-09-10T10:00:00Z", "visit1")
        tracker.record_visit("user1", "2025-09-15T10:00:00Z", "visit2")
        tracker.record_visit("user1", "2025-09-20T10:00:00Z", "visit3")
        tracker.record_visit("user1", "2025-09-25T10:00:00Z", "visit4")

        # Check visit count and surcharge
        count = tracker.get_monthly_visit_count("user1", "2025-09-25T10:00:00Z")
        should_apply = tracker.should_apply_surcharge("user1", "2025-09-25T10:00:00Z")

        assert count == 4
        assert should_apply is True

    def test_visits_in_different_months_separate_counters(self):
        """Test that visits in different months have separate counters."""
        tracker = MonthlyVisitTracker()

        # Record visits in September and October
        tracker.record_visit("user1", "2025-09-25T10:00:00Z", "visit1")
        tracker.record_visit("user1", "2025-09-30T10:00:00Z", "visit2")
        tracker.record_visit("user1", "2025-10-05T10:00:00Z", "visit3")  # New month

        # Check September count (should be 2)
        sep_count = tracker.get_monthly_visit_count("user1", "2025-09-30T10:00:00Z")
        sep_surcharge = tracker.should_apply_surcharge("user1", "2025-09-30T10:00:00Z")

        # Check October count (should be 1, no surcharge)
        oct_count = tracker.get_monthly_visit_count("user1", "2025-10-05T10:00:00Z")
        oct_surcharge = tracker.should_apply_surcharge("user1", "2025-10-05T10:00:00Z")

        assert sep_count == 2
        assert sep_surcharge is False
        assert oct_count == 1
        assert oct_surcharge is False

    def test_different_users_separate_counters(self):
        """Test that different users have separate visit counters."""
        tracker = MonthlyVisitTracker()

        # Record visits for two different users
        tracker.record_visit("user1", "2025-09-15T10:00:00Z", "visit1")
        tracker.record_visit("user1", "2025-09-20T10:00:00Z", "visit2")
        tracker.record_visit("user2", "2025-09-20T10:00:00Z", "visit3")

        # Check counts for each user
        user1_count = tracker.get_monthly_visit_count("user1", "2025-09-20T10:00:00Z")
        user2_count = tracker.get_monthly_visit_count("user2", "2025-09-20T10:00:00Z")

        assert user1_count == 2
        assert user2_count == 1

    def test_apply_monthly_surcharge_calculation(self):
        """Test the actual surcharge calculation (5% of base price)."""
        tracker = MonthlyVisitTracker()
        base_price = Price(10.00, Currency.EUR)

        # Record three visits to trigger surcharge
        tracker.record_visit("user1", "2025-09-15T10:00:00Z", "visit1")
        tracker.record_visit("user1", "2025-09-20T10:00:00Z", "visit2")
        tracker.record_visit("user1", "2025-09-25T10:00:00Z", "visit3")

        # Apply surcharge
        final_price = tracker.apply_monthly_surcharge(
            base_price, "user1", "2025-09-25T10:00:00Z"
        )

        # Expected: 10.00 + (10.00 * 0.05) = 10.50
        assert final_price.amount == 10.50
        assert final_price.currency == Currency.EUR

    def test_no_surcharge_when_less_than_three_visits(self):
        """Test that no surcharge is applied when there are fewer than 3 visits."""
        tracker = MonthlyVisitTracker()
        base_price = Price(10.00, Currency.EUR)

        # Record only two visits
        tracker.record_visit("user1", "2025-09-15T10:00:00Z", "visit1")
        tracker.record_visit("user1", "2025-09-20T10:00:00Z", "visit2")

        # Apply surcharge (should be none)
        final_price = tracker.apply_monthly_surcharge(
            base_price, "user1", "2025-09-20T10:00:00Z"
        )

        # Price should remain unchanged
        assert final_price.amount == 10.00
        assert final_price.currency == Currency.EUR

    def test_clear_all_visits(self):
        """Test that clearing visits resets all counters."""
        tracker = MonthlyVisitTracker()

        # Record some visits
        tracker.record_visit("user1", "2025-09-15T10:00:00Z", "visit1")
        tracker.record_visit("user1", "2025-09-20T10:00:00Z", "visit2")
        tracker.record_visit("user2", "2025-09-20T10:00:00Z", "visit3")

        # Verify visits are recorded
        assert tracker.get_monthly_visit_count("user1", "2025-09-20T10:00:00Z") == 2
        assert tracker.get_monthly_visit_count("user2", "2025-09-20T10:00:00Z") == 1

        # Clear all visits
        tracker.clear_all_visits()

        # Verify all visits are cleared
        assert tracker.get_monthly_visit_count("user1", "2025-09-20T10:00:00Z") == 0
        assert tracker.get_monthly_visit_count("user2", "2025-09-20T10:00:00Z") == 0

    def test_unique_visit_ids_in_same_month(self):
        """Test that duplicate visit IDs in the same month are handled correctly."""
        tracker = MonthlyVisitTracker()

        # Record the same visit ID twice (should only count once due to set behavior)
        tracker.record_visit("user1", "2025-09-15T10:00:00Z", "visit1")
        tracker.record_visit("user1", "2025-09-20T10:00:00Z", "visit1")  # Same ID

        # Should still only count as 1 visit
        count = tracker.get_monthly_visit_count("user1", "2025-09-20T10:00:00Z")
        assert count == 1

    def test_edge_case_month_boundary(self):
        """Test behavior around month boundaries."""
        tracker = MonthlyVisitTracker()

        # Record visits at end of September and beginning of October
        tracker.record_visit("user1", "2025-09-30T23:59:59Z", "visit1")
        tracker.record_visit("user1", "2025-10-01T00:00:01Z", "visit2")

        # These should be in different months
        sep_count = tracker.get_monthly_visit_count("user1", "2025-09-30T23:59:59Z")
        oct_count = tracker.get_monthly_visit_count("user1", "2025-10-01T00:00:01Z")

        assert sep_count == 1
        assert oct_count == 1
