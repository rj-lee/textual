from __future__ import annotations

from fractions import Fraction
from typing import cast

from textual.geometry import Size, Offset, Region
from textual._layout import ArrangeResult, Layout, WidgetPlacement

from textual.widget import Widget


class HorizontalLayout(Layout):
    """Used to layout Widgets horizontally on screen, from left to right. Since Widgets naturally
    fill the space of their parent container, all widgets used in a horizontal layout should have a specified.
    """

    name = "horizontal"

    def arrange(self, parent: Widget, size: Size) -> ArrangeResult:

        placements: list[WidgetPlacement] = []
        add_placement = placements.append

        x = max_width = max_height = 0
        parent_size = parent.size

        children = list(parent.children)
        styles = [child.styles for child in children if child.styles.width is not None]
        total_fraction = sum(
            [int(style.width.value) for style in styles if style.width.is_fraction]
        )
        fraction_unit = Fraction(size.height, total_fraction or 1)

        box_models = [
            widget.get_box_model(size, parent_size, fraction_unit)
            for widget in cast("list[Widget]", parent.children)
        ]

        margins = [
            max((box1.margin.right, box2.margin.left))
            for box1, box2 in zip(box_models, box_models[1:])
        ]
        if box_models:
            margins.append(box_models[-1].margin.right)

        x = box_models[0].margin.left if box_models else 0

        displayed_children = parent.displayed_children

        for widget, box_model, margin in zip(displayed_children, box_models, margins):
            content_width, content_height, box_margin = box_model
            offset_y = (
                widget.styles.align_height(
                    int(content_height), size.height - box_margin.height
                )
                + box_model.margin.top
            )
            next_x = x + content_width
            region = Region(int(x), offset_y, int(next_x - int(x)), int(content_height))
            max_height = max(max_height, content_height)
            add_placement(WidgetPlacement(region, widget, 0))
            x = next_x + margin
            max_width = x

        total_region = Region(0, 0, max_width, max_height)
        add_placement(WidgetPlacement(total_region, None, 0))

        return placements, set(displayed_children)
