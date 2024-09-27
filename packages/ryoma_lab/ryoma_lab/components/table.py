from __future__ import annotations

import reflex as rx


def table(tabular_data: list[list]):
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                *[rx.table.column_header_cell(cell) for cell in tabular_data[0]],
            ),
        ),
        rx.table.body(
            *[
                rx.table.row(
                    *[
                        (
                            rx.table.row_header_cell(cell)
                            if i == 0
                            else rx.table.cell(cell)
                        )
                        for i, cell in enumerate(row)
                    ],
                )
                for row in tabular_data[1:]
            ],
        ),
    )
