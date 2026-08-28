import sys
from devliz.application import app

def test_network_folder_validator():
    validator = app.NetworkFolderValidator()
    assert validator.validate("some string") is True
    assert validator.validate(123) is False
    assert validator.validate(None) is False
    
    assert validator.correct("test") == "test"
    assert validator.correct(123) == "123"
    assert validator.correct(None) == ""

