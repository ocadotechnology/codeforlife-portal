def is_authorised_to_view_aggregated_data(u):
    return hasattr(u, "userprofile") and u.userprofile.can_view_aggregated_data
