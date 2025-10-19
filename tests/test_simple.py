def test_addition():
    """Простой тест который всегда работает"""
    assert 1 + 1 == 2

def test_list_length():
    """Еще один простой тест"""
    items = [1, 2, 3]
    assert len(items) == 3

def test_string_operations():
    """Тест строковых операций"""
    text = "fraud detection"
    assert "fraud" in text
    assert text.upper() == "FRAUD DETECTION"