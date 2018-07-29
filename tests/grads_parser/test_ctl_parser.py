# coding=utf-8
from porter.grads_parser.grads_ctl_parser import GradsCtlParser
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path


class TestGradsCtlParser(object):
    def test_gfs_postvar_ctl(self):
        ctl_file = Path(Path(__file__).parent, "data/ctl/grapes_gfs/post.ctl_2018011912_000")

        grads_ctl_parser = GradsCtlParser()
        grads_ctl_parser.parse(str(ctl_file))

        grads_ctl = grads_ctl_parser.grads_ctl

        assert (grads_ctl.dset ==
                str(Path(Path(__file__).parent, "data/ctl/grapes_gfs/postvar2018011912_000")))

        assert (grads_ctl.title == "post output from grapes")

        assert (grads_ctl.undef == -9999.0)
