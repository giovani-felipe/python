import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.allocation.domain.model import OrderLine
from src.allocation.service_layer.unit_of_work import SqlAlchemyUnitOfWork


def insert_batch(session: Session, ref, sku, qty, eta):
    session.execute(text('INSERT INTO batches (reference, sku, purchased_quantity, eta) '
                         'VALUES (:ref, :sku, :qty, :eta)'), dict(ref=ref, sku=sku, qty=qty, eta=eta))


def get_allocated_batch_ref(session: Session, orderid, sku):
    [[orderlineid]] = session.execute(text('SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku'),
                                      dict(orderid=orderid, sku=sku))
    [[batchref]] = session.execute(text('SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id '
                                        'WHERE orderline_id=:orderlineid'), dict(orderlineid=orderlineid))
    return batchref


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session, 'batch1', 'HIPSTER-WORKBENCH', 100, None)

    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        batch = uow.batches.get(sku='HIPSTER-WORKBENCH')
        line = OrderLine('order1', 'HIPSTER-WORKBENCH', 10)
        batch.allocate(line)

    batchref = get_allocated_batch_ref(session, 'order1', 'HIPSTER-WORKBENCH')
    assert batchref == 'batch1'


# def test_rolls_back_uncommitted_work_by_default(session_factory):
#     uow = SqlAlchemyUnitOfWork(session_factory)
#     with uow:
#         insert_batch(uow.session, 'batch1', 'MEDIUM-PLINTH', 100, None)
#
#     new_session = session_factory()
#     rows = list(new_session.execute(text('SELECT * FROM "batches"')))
#     assert rows == []


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_batch(uow.session, 'batch1', 'LARGE-FORK', 100, None)
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []


def test_get_batches_without_params(session_factory):
    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        batch = uow.batches.get()

    assert batch is None
