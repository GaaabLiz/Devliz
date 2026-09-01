
def test_action_history(monkeypatch, tmp_path):
    db_path = tmp_path / "test_history.db"
    
    # Need to patch app before importing action_history because it's imported at module level
    import devliz.application.app
    monkeypatch.setattr(devliz.application.app.app, "get_path", lambda: str(tmp_path))
    
    import devliz.application.action_history as ah
    monkeypatch.setattr(ah, "PATH_ACTION_HISTORY_DB", db_path)
    
    ah.init_action_history_db()
    
    # enum
    ah.log_action(ah.ActionCategory.DASHBOARD, ah.ActionType.DASHBOARD_F5_PRESSED, "details")
    
    # str
    ah.log_action("CustomScreen", "CustomAction", "CustomDetails")
    
    actions = ah.list_actions()
    
    assert len(actions) == 2
    
    assert actions[0]["screen_key"] == "CustomScreen"
    assert actions[0]["action_key"] == "CustomAction"
    assert actions[0]["details"] == "CustomDetails"
    
    assert actions[1]["screen_key"] == "Dashboard"
    assert actions[1]["action_key"] == "dashboard.f5.pressed"
    assert actions[1]["details"] == "details"

