import pytest
from tome.api.output import TomeOutput


@pytest.mark.parametrize(
    "method, prefix", [("status", ""), ("info", ""), ("warning", "Warning: "), ("error", "Error: ")]
)
def test_regular_output(capsys, method, prefix):
    tome_output = TomeOutput()
    getattr(tome_output, method)("Una olla de algo mas vaca que carnero")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == f"{prefix}Una olla de algo mas vaca que carnero\n"
