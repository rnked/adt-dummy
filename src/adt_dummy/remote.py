"""Helpers for commands intended to run in-cluster."""

from adt_dummy.core.env import is_in_cluster


def running_in_cluster():
    return is_in_cluster()
