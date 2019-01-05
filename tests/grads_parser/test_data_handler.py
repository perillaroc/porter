# coding: utf-8
import pytest
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

from porter.grads_parser.grads_ctl_parser import GradsCtlParser
from porter.grads_parser.grads_data_handler import GradsDataHandler


class TestDataHandler(object):
    test_ctl_path = Path(Path(__file__).parent.parent, "data/sample/meso_postvar_sample.ctl")

    def test_get_offset_by_record_index(self):
        ctl_parser = GradsCtlParser()
        ctl_parser.parse(str(self.test_ctl_path))
        grads_ctl = ctl_parser.grads_ctl

        data_handler = GradsDataHandler(grads_ctl)

        assert data_handler.get_offset_by_record_index(0) == 0
        assert data_handler.get_offset_by_record_index(3) == (751 * 501 + 2) * 4 * 3

        with pytest.raises(ValueError):
            data_handler.get_offset_by_record_index(6)

    def test_get_record_by_index(self):
        ctl_parser = GradsCtlParser()
        ctl_parser.parse(str(self.test_ctl_path))
        grads_ctl = ctl_parser.grads_ctl

        data_handler = GradsDataHandler(grads_ctl)

        assert data_handler.get_record_by_index(0, 0) == 0
        assert data_handler.get_record_by_index(1, 1) == 4

        with pytest.raises(ValueError):
            data_handler.get_record_by_index(0, 3)

        with pytest.raises(ValueError):
            data_handler.get_record_by_index(2, 0)

    def test_get_offset_by_index(self):
        ctl_parser = GradsCtlParser()
        ctl_parser.parse(str(self.test_ctl_path))
        grads_ctl = ctl_parser.grads_ctl

        data_handler = GradsDataHandler(grads_ctl)

        assert data_handler.get_offset_by_index(0, 0) == 0
        assert data_handler.get_offset_by_index(1, 1) == (751 * 501 + 2) * 4 * 4

        with pytest.raises(ValueError):
            data_handler.get_offset_by_index(0, 3)

        with pytest.raises(ValueError):
            data_handler.get_offset_by_index(2, 0)

    def test_find_record(self):
        ctl_parser = GradsCtlParser()
        ctl_parser.parse(str(self.test_ctl_path))
        grads_ctl = ctl_parser.grads_ctl

        data_handler = GradsDataHandler(grads_ctl)

        assert data_handler.find_record('t', 1000.0) == 0
        assert data_handler.find_record('t', 975.0) == 1
        assert data_handler.find_record('t', 950.0) == 2
        assert data_handler.find_record('h', 1000.0) == 3
        assert data_handler.find_record('h', 975.0) == 4
        assert data_handler.find_record('h', 950.0) == 5

        assert data_handler.find_record('t', 925.0) == -1
        assert data_handler.find_record('u', 1000.0) == -1
