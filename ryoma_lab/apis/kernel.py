import reflex as rx
from sqlmodel import delete

from ryoma_lab.models.kernel import Kernel


def clear_kernels():
    with rx.session() as session:
        session.exec(delete(Kernel))
        session.commit()
