from tome.internal.cli.emojinator import Emojinator


def test_get_emoji():
    emojinator = Emojinator()

    # Test that known namespaces return the correct emoji
    assert emojinator.get_emoji("python") == "🐍"
    assert emojinator.get_emoji("docker") == "🐳"

    # Test that an unknown namespace returns an emoji (we can't predict which one because it's based on a hash)
    assert isinstance(emojinator.get_emoji("unknown"), str)
    assert emojinator.get_emoji("unknown") in emojinator.default_emojis


def test_get_hashed_emoji():
    emojinator = Emojinator()

    # Test that the same namespace always returns the same emoji
    assert emojinator.get_hashed_emoji("test_namespace") == emojinator.get_hashed_emoji("test_namespace")

    # Test that different namespaces return different emojis
    assert emojinator.get_hashed_emoji("test_namespace1") != emojinator.get_hashed_emoji("test_namespace2")
