import json

import pytest
from tenacity import Retrying, stop_after_delay

from tests.e2e import api_client, redis_client
from tests.e2e.test_api import random_orderid
from tests.util import random_sku, random_batchref


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_redis_pubsub")
def test_change_batch_quantity_leading_to_reallocation(client):
    # start with two batches and an order allocated to one of them
    orderid, sku = random_orderid(), random_sku()
    earlier_batch, later_batch = random_batchref('old'), random_batchref('newer')
    api_client.post_to_add_batch(earlier_batch, sku, qty=10, eta='2024-09-27', client=client)
    api_client.post_to_add_batch(later_batch, sku, qty=10, eta='2024-09-28', client=client)

    subscription = redis_client.subscribe_to('line_allocated')

    response = api_client.post_to_allocate(orderid, sku, 10, client=client)
    assert response.json['batchref'] == earlier_batch



    # change quantity on allocated batch so it's less than our order
    redis_client.publish_message('change_batch_quantity', {
        'batchref': earlier_batch, 'qty': 5
    })

    # wait until we see a message saying the order has been reallocated
    messages = []
    for attempt in Retrying(stop=stop_after_delay(3), reraise=True):
        with attempt:
            message = subscription.get_message(timeout=1)
            if message:
                messages.append(message)
                print(message)
            data = json.loads(messages[-1]['data'])
            assert data['orderid'] == orderid
            assert data['batchref'] == earlier_batch
