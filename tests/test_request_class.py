import pytest
from fastapi import Depends

from fastapi_jsonrpc import Entrypoint, get_jsonrpc_method, JsonRpcRequest


@pytest.fixture
def ep(ep_path):

    class CustomJsonRpcRequest(JsonRpcRequest):
        extra_value: str


    ep = Entrypoint(
        ep_path,
        request_class=CustomJsonRpcRequest
    )

    @ep.method()
    def probe(
        jsonrpc_method: str = Depends(get_jsonrpc_method),
    ) -> str:
        return jsonrpc_method

    return ep


def test_custom_request_class(ep, json_request):
    resp = json_request({
        'id': 0,
        'jsonrpc': '2.0',
        'method': 'probe',
        'params': {},
        'extra_value': 'test',
    })
    assert resp == {'id': 0, 'jsonrpc': '2.0', 'result': 'probe'}


def test_custom_request_class_unexpeted_type(ep, json_request):
    resp = json_request({
        'id': 0,
        'jsonrpc': '2.0',
        'method': 'probe',
        'params': {},
        'extra_value': {},
    })
    assert resp == {
        'error': {
            'code': -32600,
            'message': 'Invalid Request',
            'data': {'errors': [{'loc': ['extra_value'], 'msg': 'str type expected', 'type': 'type_error.str'}]},
        },
        'id': 0,
        'jsonrpc': '2.0',
    }

def test_unexpected_extra(ep, json_request):
    resp = json_request({
        'id': 0,
        'jsonrpc': '2.0',
        'method': 'echo',
        'params': {'data': 'data-123'},
        'extra_value': 'test',
        'unexpected_extra': 123,
    })
    assert resp == {
        'error': {
            'code': -32600,
            'message': 'Invalid Request',
            'data': {'errors': [
                {'loc': ['unexpected_extra'], 'msg': 'extra fields not permitted', 'type': 'value_error.extra'},
            ]},
        },
        'id': 0,
        'jsonrpc': '2.0'
    }
