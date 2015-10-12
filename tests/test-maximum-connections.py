from common import *  # noqa
import aioftp


@aioftp_setup()
@with_connection
def test_multiply_connections_no_limits(loop, client, server):

    clients = [aioftp.Client(loop=loop) for _ in range(4)]
    for client in clients:

        yield from client.connect("127.0.0.1", PORT)
        yield from client.login()

    for client in clients:

        yield from client.quit()


@aioftp_setup(
    server_args=([(aioftp.User(maximum_connections=4),)], {}))
@expect_codes_in_exception("530")
@with_connection
def test_multiply_connections_limited_error(loop, client, server):

    clients = [aioftp.Client(loop=loop) for _ in range(5)]
    for client in clients:

        yield from client.connect("127.0.0.1", PORT)
        yield from client.login()

    for client in clients:

        yield from client.quit()


@aioftp_setup(
    server_args=([(aioftp.User("foo", maximum_connections=4),)], {}))
@expect_codes_in_exception("530")
@with_connection
def test_multiply_connections_with_user_limited_error(loop, client, server):

    clients = [aioftp.Client(loop=loop) for _ in range(5)]
    for client in clients:

        yield from client.connect("127.0.0.1", PORT)
        yield from client.login("foo")

    for client in clients:

        yield from client.quit()


@aioftp_setup(
    server_args=([(aioftp.User("foo", maximum_connections=4),)], {}))
@with_connection
def test_multiply_connections_relogin_balanced(loop, client, server):

    clients = [aioftp.Client(loop=loop) for _ in range(5)]
    for client in clients[:-1]:

        yield from client.connect("127.0.0.1", PORT)
        yield from client.login("foo")

    yield from clients[0].quit()
    yield from clients[-1].connect("127.0.0.1", PORT)
    yield from clients[-1].login("foo")

    for client in clients[1:]:

        yield from client.quit()


@aioftp_setup(
    server_args=([], {"maximum_connections": 5}))
@with_connection
@expect_codes_in_exception("421")
def test_multiply_connections_server_limit_error(loop, client, server):

    clients = [aioftp.Client(loop=loop) for _ in range(5)]
    for client in clients:

        yield from client.connect("127.0.0.1", PORT)
        # yield from client.login("foo")

    for client in clients:

        yield from client.quit()


@aioftp_setup(
    server_args=([], {"maximum_connections": 5}))
@with_connection
def test_multiply_connections_server_relogin_balanced(loop, client, server):

    clients = [aioftp.Client(loop=loop) for _ in range(5)]
    for client in clients[:-1]:

        yield from client.connect("127.0.0.1", PORT)

    yield from clients[0].quit()
    yield from clients[-1].connect("127.0.0.1", PORT)

    for client in clients[1:]:

        yield from client.quit()


if __name__ == "__main__":

    import logging
    import os

    os.environ["AIOFTP_TESTS"] = "PathIO"
    logging.basicConfig(
        level=logging.INFO
    )

    test_multiply_connections_server_relogin_balanced()
    print("done")
