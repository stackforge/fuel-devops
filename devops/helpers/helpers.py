#    Copyright 2013 - 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import absolute_import

from functools import partial
# pylint: disable=redefined-builtin
from functools import reduce
# pylint: enable=redefined-builtin
import os
import socket
import time
from warnings import warn

# pylint: disable=import-error
# noinspection PyUnresolvedReferences
from six.moves import http_client
# noinspection PyUnresolvedReferences
from six.moves import xmlrpc_client
# pylint: enable=import-error


from devops.error import AuthenticationError
from devops.error import DevopsError
from devops.error import TimeoutError
from devops.helpers.ssh_client import SSHClient
from devops import logger
from devops.settings import SSH_CREDENTIALS
from devops.settings import SSH_SLAVE_CREDENTIALS


def get_free_port():
    for port in range(32000, 32100):
        if not tcp_ping('localhost', port):
            return port
    raise DevopsError('No free ports available')


def icmp_ping(host, timeout=1):
    """Run ICMP ping

    returns True if host is pingable
    False - otherwise.
    """
    return os.system(
        "ping -c 1 -W '%(timeout)d' '%(host)s' 1>/dev/null 2>&1" % {
            'host': host, 'timeout': timeout}) == 0


def tcp_ping_(host, port, timeout=None):
    s = socket.socket()
    if timeout:
        s.settimeout(timeout)
    s.connect((str(host), int(port)))
    s.close()


def _tcp_ping(*args, **kwargs):
    logger.warning('_tcp_ping is deprecated in favor of tcp_ping_')
    warn('_tcp_ping is deprecated in favor of tcp_ping_', DeprecationWarning)
    return tcp_ping_(*args, **kwargs)


def tcp_ping(host, port, timeout=None):
    """Run TCP ping

    returns True if TCP connection to specified host and port
    can be established
    False - otherwise.
    """
    try:
        tcp_ping_(host, port, timeout)
    except socket.error:
        return False
    return True


def wait(predicate, interval=5, timeout=60, timeout_msg="Waiting timed out"):
    """Wait until predicate will become True.

    returns number of seconds that is left or 0 if timeout is None.

    Options:

    interval - seconds between checks.

    timeout  - raise TimeoutError if predicate won't become True after
    this amount of seconds. 'None' disables timeout.

    timeout_msg - text of the TimeoutError

    """
    start_time = time.time()
    if not timeout:
        return predicate()
    while not predicate():
        if start_time + timeout < time.time():
            raise TimeoutError(timeout_msg)

        seconds_to_sleep = max(
            0,
            min(interval, start_time + timeout - time.time()))
        time.sleep(seconds_to_sleep)

    return timeout + start_time - time.time()


def wait_pass(raising_predicate, expected=Exception, interval=5, timeout=None):
    """Wait for successful return from predicate or expected exception"""
    start_time = time.time()
    while True:
        try:
            return raising_predicate()
        except expected:
            if timeout and start_time + timeout < time.time():
                raise
            time.sleep(interval)


def _wait(*args, **kwargs):
    logger.warning('_wait has been deprecated in favor of wait_pass')
    warn('_wait has been deprecated in favor of wait_pass', DeprecationWarning)
    return wait_pass(*args, **kwargs)


def wait_tcp(host, port, timeout, timeout_msg="Waiting timed out"):
    is_port_active = partial(tcp_ping, host=host, port=port)
    wait(is_port_active, timeout=timeout, timeout_msg=timeout_msg)


def wait_ssh_cmd(
        host,
        port,
        check_cmd,
        username=SSH_CREDENTIALS['login'],
        password=SSH_CREDENTIALS['password'],
        timeout=0):
    ssh_client = SSHClient(host=host, port=port,
                           username=username,
                           password=password)
    wait(lambda: not ssh_client.execute(check_cmd)['exit_code'],
         timeout=timeout)


def http(host='localhost', port=80, method='GET', url='/', waited_code=200):
    try:
        conn = http_client.HTTPConnection(str(host), int(port))
        conn.request(method, url)
        res = conn.getresponse()

        return res.status == waited_code
    except Exception:
        return False


def get_private_keys(env):
    logger.warning(
        'get_private_keys has been deprecated in favor of DevopsClient')
    warn(
        'get_private_keys has been deprecated in favor of DevopsClient',
        DeprecationWarning)

    from devops.client import DevopsClient
    client = DevopsClient(env_name=env.name)
    return client.get_private_keys()


def get_admin_remote(env, login=SSH_CREDENTIALS['login'],
                     password=SSH_CREDENTIALS['password']):
    logger.warning(
        'get_admin_remote has been deprecated in favor of DevopsClient')
    warn(
        'get_admin_remote has been deprecated in favor of DevopsClient',
        DeprecationWarning)

    from devops.client import DevopsClient
    client = DevopsClient(env_name=env.name)
    return client.get_admin_remote(login=login, password=password)


def get_node_remote(env, node_name, login=SSH_SLAVE_CREDENTIALS['login'],
                    password=SSH_SLAVE_CREDENTIALS['password']):
    logger.warning(
        'get_node_remote has been deprecated in favor of DevopsClient')
    warn(
        'get_node_remote has been deprecated in favor of DevopsClient',
        DeprecationWarning)

    from devops.client import DevopsClient
    client = DevopsClient(env_name=env.name)
    return client.get_node_remote(
        node_name=node_name, login=login, password=password)


def get_admin_ip(env):
    logger.warning(
        'get_admin_ip has been deprecated in favor of DevopsClient')
    warn(
        'get_admin_ip has been deprecated in favor of DevopsClient',
        DeprecationWarning)

    from devops.client import DevopsClient
    client = DevopsClient(env_name=env.name)
    return client.get_admin_ip()


def get_slave_ip(env, node_mac_address):
    logger.warning('get_slave_ip has been deprecated in favor of '
                   'DevopsClient.get_node_ip')
    warn('get_slave_ip has been deprecated in favor of '
         'DevopsClient.get_node_ip', DeprecationWarning)

    from devops.client import DevopsClient
    from devops.client import NailgunClient
    client = DevopsClient(env_name=env.name)
    ng_client = NailgunClient(ip=client.get_admin_ip())
    return ng_client.get_slave_ip_by_mac(node_mac_address)


def ssh(*args, **kwargs):
    warn(
        'devops.helpers.ssh is deprecated '
        'and will be removed soon', DeprecationWarning)
    return SSHClient(*args, **kwargs)


def xmlrpctoken(uri, login, password):
    server = xmlrpc_client.Server(uri)
    try:
        return server.login(login, password)
    except Exception:
        raise AuthenticationError("Error occurred while login process")


def xmlrpcmethod(uri, method):
    server = xmlrpc_client.Server(uri)
    try:
        return getattr(server, method)
    except Exception:
        raise AttributeError("Error occurred while getting server method")


def generate_mac():
    return "64:{0:02x}:{1:02x}:{2:02x}:{3:02x}:{4:02x}".format(
        *bytearray(os.urandom(5)))


def get_file_size(path):
    """Get size of file-like object

    :type path: str
    :rtype : int
    """

    return os.stat(path).st_size


def _get_file_size(*args, **kwargs):
    logger.warning(
        '_get_file_size has been deprecated in favor of get_file_size')
    warn(
        '_get_file_size has been deprecated in favor of get_file_size',
        DeprecationWarning)
    return get_file_size(*args, **kwargs)


def deepgetattr(obj, attr, default=None, splitter='.', do_raise=False):
    """Recurses through an attribute chain to get the ultimate value.

    :type obj: object
    :param obj: object instance to get attribute from
    :type attr: str
    :param attr: attributes joined by some symbol. e.g. 'a.b.c.d'
    :type default: any
    :param default: default value (returned only in case of
                    AttributeError)
    :type splitter: str
    :param splitter: one or more symbols to be used to split attr
                     parameter
    :type do_raise: bool
    :param do_raise: if True then instead of returning default value
                     AttributeError will be raised

    """
    try:
        return reduce(getattr, attr.split(splitter), obj)
    except AttributeError:
        if do_raise:
            raise
        return default


def underscored(*args):
    """Joins multiple strings using uderscore symbol.

       Skips empty strings.
    """
    return '_'.join(filter(bool, list(args)))


def get_nodes(admin_ip):
    logger.warning('get_nodes has been deprecated in favor of '
                   'NailgunClient.get_nodes_json')
    warn('get_nodes has been deprecated in favor of '
         'NailgunClient.get_nodes_json', DeprecationWarning)

    from devops.client import NailgunClient
    ng_client = NailgunClient(ip=admin_ip)
    return ng_client.get_nodes_json()
