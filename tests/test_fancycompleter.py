from fancycompleter import Color, Completer, DefaultConfig, commonprefix
from fancycompleter.__main__ import Installer


class ConfigForTest(DefaultConfig):
    use_colors = False


class ColorConfig(DefaultConfig):
    use_colors = True


def test_commonprefix():
    assert commonprefix(["isalpha", "isdigit", "foo"]) == ""
    assert commonprefix(["isalpha", "isdigit"]) == "is"
    assert commonprefix(["isalpha", "isdigit", "foo"], base="i") == "is"
    assert commonprefix([]) == ""
    assert commonprefix(["aaa", "bbb"], base="x") == ""


def test_complete_attribute():
    compl = Completer({"a": None}, ConfigForTest)
    assert compl.attr_matches("a.") == ["a.__"]
    matches = compl.attr_matches("a.__")
    assert "a.__class__" not in matches
    assert "__class__" in matches
    assert compl.attr_matches("a.__class") == ["a.__class__"]


def test_complete_attribute_prefix():
    class C:
        attr = 1
        _attr = 2
        __attr__attr = 3

    compl = Completer({"a": C}, ConfigForTest)
    assert compl.attr_matches("a.") == ["attr", "mro"]
    assert compl.attr_matches("a._") == ["_C__attr__attr", "_attr", " "]
    matches = compl.attr_matches("a.__")
    assert "a.__class__" not in matches
    assert "__class__" in matches
    assert compl.attr_matches("a.__class") == ["a.__class__"]

    compl = Completer({"a": None}, ConfigForTest)
    assert compl.attr_matches("a._") == ["a.__"]


def test_complete_attribute_colored():
    compl = Completer({"a": 42}, ColorConfig)
    matches = compl.attr_matches("a.__")
    assert len(matches) > 2
    expected_color = compl.config.color_by_type.get(type(compl.__class__))
    assert expected_color == "35;01"
    expected_part = Color.set(expected_color, "__class__")
    for match in matches:
        if expected_part in match:
            break
    else:
        assert False, matches
    assert " " in matches


def test_complete_colored_single_match():
    """No coloring, via commonprefix."""
    compl = Completer({"foobar": 42}, ColorConfig)
    matches = compl.global_matches("foob")
    assert matches == ["foobar"]


def test_does_not_color_single_match():
    class obj:
        msgs = []

    compl = Completer({"obj": obj}, ColorConfig)
    matches = compl.attr_matches("obj.msgs")
    assert matches == ["obj.msgs"]


def test_complete_global():
    compl = Completer({"foobar": 1, "foobazzz": 2}, ConfigForTest)
    assert compl.global_matches("foo") == ["fooba"]
    matches = compl.global_matches("fooba")
    assert set(matches) == {"foobar", "foobazzz"}
    assert compl.global_matches("foobaz") == ["foobazzz"]
    assert compl.global_matches("nothing") == []


def test_complete_global_colored():
    compl = Completer({"foobar": 1, "foobazzz": 2}, ColorConfig)
    assert compl.global_matches("foo") == ["fooba"]
    matches = compl.global_matches("fooba")
    assert set(matches) == {
        " ",
        "\x1b[001;00m\x1b[33;01mfoobazzz\x1b[00m",
        "\x1b[000;00m\x1b[33;01mfoobar\x1b[00m",
    }
    assert compl.global_matches("foobaz") == ["foobazzz"]
    assert compl.global_matches("nothing") == []


def test_complete_global_colored_exception():
    compl = Completer({"tryme": ValueError()}, ColorConfig)
    assert compl.global_matches("try") == [
        "\x1b[000;00m\x1b[37mtry:\x1b[00m",
        "\x1b[001;00m\x1b[31;01mtryme\x1b[00m",
        " ",
    ]


def test_complete_global_exception(monkeypatch):
    import rlcompleter

    def rlcompleter_global_matches(self, text):
        return ["trigger_exception!", "nameerror", "valid"]

    monkeypatch.setattr(
        rlcompleter.Completer, "global_matches", rlcompleter_global_matches
    )

    compl = Completer({"valid": 42}, ColorConfig)
    assert compl.global_matches("") == [
        "\x1b[000;00m\x1b[31;01mnameerror\x1b[00m",
        "\x1b[001;00m\x1b[31;01mtrigger_exception!\x1b[00m",
        "\x1b[002;00m\x1b[33;01mvalid\x1b[00m",
        " ",
    ]


def test_color_for_obj(monkeypatch):
    class Config(ColorConfig):
        color_by_type = {}

    compl = Completer({}, Config)
    assert compl.color_for_obj(1, "foo", "bar") == "\x1b[001;00m\x1b[00mfoo\x1b[00m"


def test_complete_with_indexer():
    compl = Completer({"lst": [None, 2, 3]}, ConfigForTest)
    assert compl.attr_matches("lst[0].") == ["lst[0].__"]
    matches = compl.attr_matches("lst[0].__")
    assert "lst[0].__class__" not in matches
    assert "__class__" in matches
    assert compl.attr_matches("lst[0].__class") == ["lst[0].__class__"]


def test_autocomplete():
    class A:
        aaa = None
        abc_1 = None
        abc_2 = None
        abc_3 = None
        bbb = None

    compl = Completer({"A": A}, ConfigForTest)
    #
    # in this case, we want to display all attributes which start with
    # 'a'. MOREOVER, we also include a space to prevent readline to
    # automatically insert the common prefix (which will the the ANSI escape
    # sequence if we use colors)
    matches = compl.attr_matches("A.a")
    assert sorted(matches) == [" ", "aaa", "abc_1", "abc_2", "abc_3"]
    #
    # IF there is an actual common prefix, we return just it, so that readline
    # will insert it into place
    matches = compl.attr_matches("A.ab")
    assert matches == ["A.abc_"]
    #
    # finally, at the next TAB, we display again all the completions available
    # for this common prefix. Again, we insert a spurious space to prevent the
    # automatic completion of ANSI sequences
    matches = compl.attr_matches("A.abc_")
    assert sorted(matches) == [" ", "abc_1", "abc_2", "abc_3"]


def test_complete_exception():
    compl = Completer({}, ConfigForTest)
    assert compl.attr_matches("xxx.") == []


def test_complete_invalid_attr():
    compl = Completer({"str": str}, ConfigForTest)
    assert compl.attr_matches("str.xx") == []


def test_complete_function_skipped():
    compl = Completer({"str": str}, ConfigForTest)
    assert compl.attr_matches("str.split().") == []


def test_dir():
    class Foo:
        def __dir__(self):
            return ["hello", "world"]

    compl = Completer({"a": Foo()}, ConfigForTest)
    matches = compl.attr_matches("a.")
    assert matches == ["hello", "world"]


class MyInstaller(Installer):
    env_var = 0

    def set_env_var(self):
        self.env_var += 1


class TestInstaller:
    def test_check(self, monkeypatch, tmpdir):
        installer = MyInstaller(str(tmpdir), force=False)
        monkeypatch.setenv("PYTHONSTARTUP", "")
        assert installer.check() is None
        f = tmpdir.join("python_startup.py").ensure(file=True)
        assert installer.check() == f"{f} already exists"
        monkeypatch.setenv("PYTHONSTARTUP", "foo")
        assert installer.check() == "PYTHONSTARTUP already defined: foo"

    def test_install(self, monkeypatch, tmpdir):
        installer = MyInstaller(str(tmpdir), force=False)
        monkeypatch.setenv("PYTHONSTARTUP", "")
        assert installer.install()
        assert "fancycompleter" in tmpdir.join("python_startup.py").read()
        assert installer.env_var == 1
        #
        # the second time, it fails because the file already exists
        assert not installer.install()
        assert installer.env_var == 1
        #
        # the third time, it succeeds because we set force
        installer.force = True
        assert installer.install()
        assert installer.env_var == 2
