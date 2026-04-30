import sys
import types


def test_set_and_get_language():
    from devliz.application import i18n

    i18n.set_language("it")
    assert i18n.get_language() == "it"

    i18n.set_language("en")
    assert i18n.get_language() == "en"


def test_tr_returns_translated_text_for_italian():
    from devliz.application import i18n

    i18n.set_language("it")
    assert i18n.tr("Search") == "Cerca"


def test_tr_falls_back_to_key_for_unknown_entry():
    from devliz.application import i18n

    i18n.set_language("it")
    assert i18n.tr("Unknown key") == "Unknown key"


def test_tr_formats_placeholders_and_ignores_missing_kwargs():
    from devliz.application import i18n

    i18n.set_language("it")
    assert i18n.tr("Total configurations: {count} ({size})", count=3, size="10 MB") == "Totale configurazioni: 3 (10 MB)"

    # Se manca un placeholder, la stringa resta invariata senza eccezioni
    assert i18n.tr("Total configurations: {count} ({size})", count=3) == "Totale configurazioni: {count} ({size})"


def test_init_language_reads_saved_setting(monkeypatch):
    from devliz.application import i18n

    fake_app_module = types.ModuleType("devliz.application.app")

    class FakeAppSettings:
        @staticmethod
        def get(_key):
            return "it"

    class FakeAppSettingsKeys:
        language = "language"

    fake_app_module.app_settings = FakeAppSettings()
    fake_app_module.AppSettings = FakeAppSettingsKeys
    monkeypatch.setitem(sys.modules, "devliz.application.app", fake_app_module)

    i18n.set_language("en")
    i18n.init_language()
    assert i18n.get_language() == "it"

