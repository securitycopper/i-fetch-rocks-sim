from ifetchrocks_sim import AmbiguousLabelError, LabelRegistry


def test_label_registry_exact_and_prefix_lookup():
    labels = LabelRegistry()
    labels.set("abcd1234", "pc")

    assert labels.get("abcd1234") == "pc"
    assert labels.get("abcd1234-ffff") == "pc"
    assert labels.get("abcd") == "pc"


def test_label_registry_raises_on_ambiguous_prefix():
    labels = LabelRegistry()
    labels.set("abcd1111", "a")
    labels.set("abcd2222", "b")

    try:
        labels.get("abcd")
        raised = False
    except AmbiguousLabelError:
        raised = True

    assert raised


def test_label_registry_save_and_load(tmp_path):
    labels = LabelRegistry()
    labels.set("ffff0000", "bus")

    p = tmp_path / "labels.json"
    labels.save(str(p))

    loaded = LabelRegistry()
    loaded.load(str(p))

    assert loaded.get("ffff") == "bus"
