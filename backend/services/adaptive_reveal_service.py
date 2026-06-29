def determine_reveal_state(stats):
    """
    Input stats: { 'risk_score': int, 'completion_rate': int, 'days_remaining': int }
    Returns: { 'risk_level': str, 'reveal_count': int, 'rescue_required': bool }
    """
    risk_score = stats.get('risk_score', 0)
    completion_rate = stats.get('completion_rate', 0)
    days_remaining = stats.get('days_remaining', 0)

    if risk_score >= 70 or completion_rate < 40 or days_remaining <= 2:
        return {
            "risk_level": "high",
            "reveal_count": 3,
            "rescue_required": True
        }
    elif 40 <= risk_score < 70:
        return {
            "risk_level": "medium",
            "reveal_count": 2,
            "rescue_required": False
        }
    else:
        return {
            "risk_level": "low",
            "reveal_count": 1,
            "rescue_required": False
        }

def get_visible_missions(missions, reveal_count):
    """
    Returns only the missions that should currently be visible.
    Visible missions include:
    - All completed missions
    - The first `reveal_count` incomplete missions (ordered by order_index)
    """
    # Sort missions by order_index/order
    def get_order(m):
        if hasattr(m, 'order_index'):
            return m.order_index
        if isinstance(m, dict):
            return m.get('order_index') or m.get('order') or 0
        return 0

    sorted_missions = sorted(missions, key=get_order)

    visible = []
    incomplete_revealed = 0

    for m in sorted_missions:
        is_completed = getattr(m, 'is_completed', False)
        if isinstance(m, dict):
            is_completed = m.get('is_completed', False)

        if is_completed:
            visible.append(m)
        else:
            if incomplete_revealed < reveal_count:
                visible.append(m)
                incomplete_revealed += 1

    return visible
