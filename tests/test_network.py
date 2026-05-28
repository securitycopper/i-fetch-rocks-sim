from ifetchrocks_sim.network import DataNetwork, DataNetworkManager, LargeDataNetwork


def test_data_network_or_merges_sources():
    net = DataNetwork("wire-1")
    net.register_source("a")
    net.register_source("b")

    net.update_source("a", 0b0010)
    net.update_source("b", 0b0100)

    assert net.value == 0b0110


def test_data_network_override_blocks_source_updates():
    net = DataNetwork("wire-1")
    seen = []
    net.register_listener(lambda _u, v: seen.append(v))
    net.register_source("a")

    net.update_source("a", 3)
    net.set_override(9)
    net.update_source("a", 7)
    net.clear_override()

    assert seen[0] == 0
    assert net.value == 7


def test_large_network_or_merges_sources():
    net = LargeDataNetwork("lw-1")
    net.register_source("a")
    net.register_source("b")

    a = [0] * 32
    b = [0] * 32
    a[0] = 1
    b[0] = 4

    net.update_source("a", a)
    net.update_source("b", b)

    assert net.value[0] == 5


def test_data_network_manager_flushes_queued_notifications_on_tick_change():
    manager = DataNetworkManager()
    net = manager.get_network("w")
    calls = []
    net.register_listener(lambda _u, v: calls.append(v))

    net.register_source("a")
    net.update_source("a", 1)
    manager.queue_notify(net)
    manager.set_tick(1)

    assert calls[-1] == 1
