import pytest


def test_equal_or_not_eqal():
    assert 3==3

def test_type():
    assert type("hello" is str)
    assert type("world" is not int)

def test_boolean():
    validated = True
    assert validated is True
    assert ("hello" == "World") is False

def test_greater_and_less_than():
    assert 7 > 3
    assert 4 < 10

def test_list():
    num_list = [1, 2, 3, 4, 5]
    any_list = [False, False]
    assert 1 in num_list
    assert 8 not in num_list
    assert all(num_list)
    assert not any(any_list)

class Student:
    def __init__(self, first_name: str, last_name:str, manjor:str, years: int) -> None:
        self.firstname = first_name
        self.last_name = last_name
        self.major = manjor
        self.years = years

@pytest.fixture
def default_employee():
    return Student('John', 'Doe', 'Computer Science', 3)

def test_person_initialization(default_employee):
    assert default_employee.firstname == 'John', 'First name should be John'
    assert default_employee.last_name == 'Doe', 'last name should be Doe'
    assert default_employee.major == 'Computer Science'
    assert default_employee.years == 3

