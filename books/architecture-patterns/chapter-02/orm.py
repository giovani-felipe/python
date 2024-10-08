from sqlalchemy import Column, Integer, String, Table, Date, ForeignKey
from sqlalchemy.orm import registry, relationship

from model import OrderLine, Batch

mapper_registry = registry()

order_line = Table(
    "order_lines", mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255))
)

batches = Table(
    "batches", mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True)
)

allocations = Table(
    "allocations", mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id"))
)


def start_mappers():
    lines_mapper = mapper_registry.map_imperatively(OrderLine, order_line)
    mapper_registry.map_imperatively(Batch, batches, properties={
        "_allocations": relationship(lines_mapper, secondary=allocations, collection_class=set)})
