from devliz.application import i18n

def test_i18n():
    i18n.set_language("en")
    assert i18n.get_language() == "en"
    assert i18n.tr("Home") == "Home"
    assert i18n.tr("Hello {name}", name="World") == "Hello World"
    
    i18n.set_language("it")
    assert i18n.tr("Home") == "Home"
    assert i18n.tr("Help") == "Aiuto"
    assert i18n.tr("Hello {name}", name="World") == "Hello World"
    assert i18n.tr("An error occurred: {error}", error="404") == "Si è verificato un errore: 404"
    assert i18n.tr("Missing") == "Missing"
    assert i18n.tr("Missing {val}", val=1) == "Missing 1"
    assert i18n.tr("Missing {val}", other=1) == "Missing {val}"

def test_init_language(monkeypatch):
    class FakeAppSet:
        def get(self, k): return "it"
    import devliz.application.app
    monkeypatch.setattr(devliz.application.app, "app_settings", FakeAppSet())
    
    i18n.init_language()
    assert i18n.get_language() == "it"

