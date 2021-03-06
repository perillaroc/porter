# coding=utf-8
from porter.grib_tool.base.grib_condition import GribCondition


def test_constructor():
    condition = GribCondition('typeOfLevel', 'isobaricInhPa')
    assert condition.name == 'typeOfLevel'
    assert condition.values == ['isobaricInhPa']
    assert condition.value_type == str

    condition = GribCondition('shortName', 't|v')
    assert condition.name == 'shortName'
    assert condition.values == ['t', 'v']
    assert condition.value_type == str

    condition = GribCondition('level', '1000|500')
    assert condition.name == 'level'
    assert condition.values == [1000, 500]
    assert condition.value_type == float


def mock_codes_get(message, name):
    return message[name]


def test_condition(monkeypatch):
    condition = GribCondition('shortName', 't')
    grib_message = {
        'shortName': 't'
    }
    monkeypatch.setattr(grib_message, 'getString', mock_codes_get)

    assert condition.is_fit(grib_message)


def test_multi_condition(monkeypatch):
    condition = GribCondition('shortName', 't|v|u')
    t_grib_message = {
        'shortName': 't'
    }
    monkeypatch.setattr(t_grib_message, 'getString', mock_codes_get)
    assert condition.is_fit(t_grib_message)
    v_grib_message = {
        'shortName': 'v'
    }
    monkeypatch.setattr(v_grib_message, 'getString', mock_codes_get)
    assert condition.is_fit(v_grib_message)
    h_grib_message = {
        'shortName': 'h'
    }
    monkeypatch.setattr(h_grib_message, 'getString', mock_codes_get)
    assert not condition.is_fit(h_grib_message)


def test_condition_equal():
    condition_a = GribCondition('shortName', 't|u|v')
    condition_b = GribCondition('shortName', 't|u|v')
    assert condition_a == condition_b

    condition_a = GribCondition('shortName', 't|u|v')
    condition_b = GribCondition('shortName', 't|u')
    assert not condition_a == condition_b

    condition_a = GribCondition('shortName', 't|u|v')
    condition_b = GribCondition('level', '1000,875')
    assert not condition_a == condition_b

