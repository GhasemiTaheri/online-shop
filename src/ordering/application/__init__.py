"""Ordering application layer."""

from ordering.application.create_order import create_order
from ordering.domain.commands import CreateOrder


COMMAND_HANDLERS = {
    CreateOrder: create_order,
}
