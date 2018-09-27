"""Tests for Pywowcher API methods."""

import datetime
import json
import os

import pytest
import pywowcher

TEST_URI = "test_uri"


def get_test_api_method(uri, method):
    """Return a new API method."""
    API_method = pywowcher.api_methods.api_method.BaseAPIMethod
    API_method.uri = uri
    API_method.method = method
    return API_method


def test_method_get_URL():
    """Test the get_URL method of BaseAPIMethod."""
    expected_URL = f"{pywowcher.WowcherAPISession.DOMAIN}{TEST_URI}"
    API_method = get_test_api_method(
        TEST_URI, pywowcher.api_methods.api_method.BaseAPIMethod.POST
    )
    assert expected_URL == API_method.get_URL()


def test_post_request(requests_mock):
    """Test the WowcherAPISession.make_request method."""
    response_text = "hello"
    API_method = get_test_api_method(
        TEST_URI, pywowcher.api_methods.api_method.BaseAPIMethod.POST
    )
    requests_mock.post(API_method.get_URL(), text=response_text)
    response = API_method().call()
    assert response.text == response_text


def test_get_request(requests_mock):
    """Test the WowcherAPISession.make_request method."""
    response_text = "hello"
    API_method = get_test_api_method(
        TEST_URI, pywowcher.api_methods.api_method.BaseAPIMethod.GET
    )
    requests_mock.register_uri("GET", API_method.get_URL(), text=response_text)
    response = API_method().call()
    assert response.text == response_text


@pytest.fixture
def orders_method_response():
    """Return an example response for the Orders API method."""
    with open(os.path.join(os.path.dirname(__file__), "order_response.json"), "r") as f:
        return json.load(f)


def mock_status(requests_mock):
    """Set up a mocked status request."""
    requests_mock.put(pywowcher.api_methods.Status.get_URL())


def mock_echo_test(requests_mock, message=None, response=None):
    """Set up a mocked echo test request."""
    if message is not None:
        response = {"json": echo_test_response(message)}
    elif response is None:
        raise Exception("Either kwargs or message must be passed")
    if isinstance(response, dict):
        response = [response]
    requests_mock.post(pywowcher.api_methods.EchoTest.get_URL(), response)


def mock_orders(requests_mock, response_data=None, response=None):
    """Set up a mocked orders request."""
    if response is None and response_data is None:
        response = {"json": orders_method_response()}
    elif response_data is not None:
        response = {"json": response_data}
    if isinstance(response, dict):
        response = [response]
    requests_mock.get(pywowcher.api_methods.Orders.get_URL(), response)


def echo_test_response(message):
    """Return the response from the Echo Test API method for a given message."""
    return {"message": "Echo Test Received", "data": message}


def test_echo_test_method(requests_mock):
    """Test the EchoTest API method."""
    message = {"one": "1", "two": "2"}
    mock_echo_test(requests_mock, message)
    response = pywowcher.api_methods.EchoTest(message).call()
    assert response == message


PAGE = 1
PER_PAGE = 100
FROM_DATE = datetime.datetime.now() - datetime.timedelta(days=1)
START_DATE = datetime.datetime.now() - datetime.timedelta(days=1)
END_DATE = datetime.datetime.now()
DEAL_ID = 9856321


def test_Orders_get_data_method(requests_mock):
    """Test the get_data method of Orders."""
    method = pywowcher.api_methods.Orders(
        page=PAGE,
        per_page=PER_PAGE,
        from_date=FROM_DATE,
        start_date=START_DATE,
        end_date=END_DATE,
        deal_id=DEAL_ID,
    )
    expected_data = {
        "page": PAGE,
        "per_page": PER_PAGE,
        "from_date": FROM_DATE,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "deal_id": DEAL_ID,
    }
    assert method.data == expected_data


def test_process_response_method(requests_mock, orders_method_response):
    """Test the process_response method of Orders."""
    requests_mock.get(
        pywowcher.api_methods.Orders.get_URL(), json=orders_method_response
    )
    response = pywowcher.api_methods.Orders(
        page=PAGE,
        per_page=PER_PAGE,
        from_date=FROM_DATE,
        start_date=START_DATE,
        end_date=END_DATE,
        deal_id=DEAL_ID,
    ).call()
    assert response == orders_method_response


def test_status_API_method(requests_mock):
    """Test the Status API method."""
    mock_status(requests_mock)
    orders = [
        {
            "reference": "8UPGT3-KKQRNC",
            "timestamp": 1234567890,
            "status": 2,
            "tracking_number": "JD1233230001012",
            "shipping_vendor": "ROYAL_MAIL",
            "shipping_method": "NEXT_DAY",
        }
    ]
    request = pywowcher.api_methods.Status(orders=orders)
    sent_data = request.get_data(orders=orders)
    assert pywowcher.api_methods.Status.ORDERS in sent_data
    assert sent_data[request.ORDERS][0]["reference"] == orders[0]["reference"]
    response = request.call()
    assert response.status_code == 200
