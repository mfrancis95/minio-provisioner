from docker import APIClient
from os import environ
from redis import Redis
from time import sleep

_docker = APIClient(environ.get('DOCKER_SOCKET', 'unix://var/run/docker.sock'), 'auto')
_redis = Redis(decode_responses = True)

if not _redis.exists('nextPort'):
    _redis.set('nextPort', '9000')

def _get_next_port():
    port = int(_redis.get('nextPort'))
    _redis.incr('nextPort')
    return port

def create_instance(username, name, s3_access_key, s3_secret_key):
    port = _get_next_port()
    container = _docker.create_container(
        'minio/minio', command = f'gateway s3 {environ["S3_ENDPOINT"]}',
        detach = True, environment = {
            'MINIO_ACCESS_KEY': s3_access_key,
            'MINIO_SECRET_KEY': s3_secret_key
        }, host_config = _docker.create_host_config(port_bindings = {
            9000: port
        }), name = name
    )
    _docker.start(container['Id'])
    sleep(1)
    if _docker.inspect_container(container['Id'])['State']['Status'] == 'exited':
        _docker.remove_container(container['Id'], force = True)
        return False
    _redis.hset(username, name, port)
    return True

def get_instances(username):
    return _redis.hgetall(username)