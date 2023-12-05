import numpy as np
from PIL import Image, ImageDraw

from .item import GraphItem
from .color import Color
from .utils import circle_xy, get_color, limit


class PieChart:
    """Class representing a Pie chart."""
    def __init__(self,
                 *,
                 radius: int,
                 thickness: int | None = None,
                 angle: int | None = None,
                 emboss: int | None = None,
                 space_between: int | None = None) -> None:
        """
        PieChart constructor.

        Attributes
        ----------
        radius: `int`
            Radius of the chart circle.
        thickness: `int` | `None`
            If None, graph will be pie-shaped.
            Otherwise, graph will be donut-shaped with specified thickness.
        angle: `int` | `None`
            Start angle of the chart.
        emboss: `int` | `None`
            If None, graph will be flat. 
            Otherwise, graph parts will be different size based on value.
            If < 0, parts with higher weight will be smaller.
        space: `int` | `None`
            Space between graph parts.
        """
        self.radius = radius
        self.thickness= thickness
        self.angle = angle
        self.emboss = emboss
        self.space_between = space_between
        self._items: list[GraphItem] = []

    @property
    def radius(self) -> int:
        """Chart circle radius."""
        return self._radius
    
    @radius.setter
    def radius(self, value: int):
        if (hasattr(self, '_thickness')
            and self.thickness is not None
            and self.thickness > value):
            raise ValueError("'radius' can not be smaller than 'thickness'")
        self._radius = value

    @property
    def thickness(self) -> int | None:
        """Thickness of the donut-shaped graph."""
        return self._thickness
    
    @thickness.setter
    def thickness(self, value: int | None):
        if (value is not None 
            and hasattr(self, '_radius') 
            and self.radius < value):
            raise ValueError("'thickness' can not be bigger than 'radius'")
        if (value is not None 
            and hasattr(self, '_emboss') 
            and self.emboss is not None 
            and abs(self.emboss) * 2 < value):
            raise ValueError("'thickness' can not be bigger than absolute value of 'emboss' twice")
        self._thickness = value

    @property
    def angle(self) -> int | None:
        """Chart start angle"""
        return self._angle
    
    @angle.setter
    def angle(self, value: int | None):
        self._angle = value

    @property
    def emboss(self) -> int | None:
        """Graph parts max emboss."""
        return self._emboss
    
    @emboss.setter
    def emboss(self, value: int | None):
        if (value is not None 
            and hasattr(self, '_thickness') 
            and self.thickness is not None 
            and self.thickness < abs(value) * 2):
            raise ValueError("'emboss' can not be bigger than half of 'thickness'")
        self._emboss = value

    @property
    def space_between(self) -> int | None:
        """Space between chart parts."""
        return self._space_between
    
    @space_between.setter
    def space_between(self, value: int | None):
        self._space_between = value

    @property
    def items(self) -> list[GraphItem]:
        """Chart items."""
        return self._items

    def add_items(self, *items: GraphItem) -> None:
        """
        Add items to graph.

        Attributes
        ----------
        items: `CircleGraphItem`
            Items to add.

        Raises
        ------
        `ValueError` if item is not of correct type.
        """
        for item in items:
            if not isinstance(item, GraphItem):
                raise ValueError(f"items must be instances of '{GraphItem.__name__}', not {type(item).__name__}")
            self._items.append(item)

    def remove_items(self, *items: GraphItem) -> None:
        """
        Remove items from graph.

        Attributes
        ----------
        items: `CircleGraphItem`
            Items to remove.

        Raises
        ------
        `ValueError` if item is not present.
        """
        for item in items:
            self._items.remove(item)

    def draw(self) -> Image.Image:
        """
        Draw a Pie chart.
        """
        image = Image.new('RGBA', (self.radius * 2,)*2)
        num_items = len(self.items)

        if num_items == 0:
            return image
        
        weights = np.array([item.weight for item in self.items])
        total_weight = weights.sum()
        start_angle = self.angle or 0
        thickness = self.thickness
        emboss = self.emboss or 0
        template = image.copy()

        offsets = limit(
            weights, 
            0 if emboss < 0 else abs(emboss), 
            abs(emboss) if emboss < 0 else 0)

        for i, item in enumerate(self.items):
            img = template.copy()
            draw = ImageDraw.Draw(img)
            offset = offsets[i]

            if total_weight == 0: 
                angle = 360 / num_items
            else:
                angle = 360 * item.weight / total_weight

            if item.color is not None:
                draw.pieslice(((0 + offset,)*2, (img.width - offset,)*2),
                            start_angle, start_angle + angle,
                            fill=item.color.rgba)
                
                if self.space_between:
                    draw.line(((self.radius,)*2, circle_xy(self.radius, self.radius, start_angle + angle)),
                            fill=(0, 0, 0, 0), width=self.space_between)
                    draw.line(((self.radius,)*2, circle_xy(self.radius, self.radius, start_angle)),
                            fill=(0, 0, 0, 0), width=self.space_between)
                    draw.ellipse(((self.radius - self.space_between / 2,)*2, (self.radius + self.space_between / 2,)*2),
                                fill=(0, 0, 0, 0), width=0)
            
                if thickness:
                    draw.ellipse(((thickness - offset,)*2, (self.radius * 2 - thickness + offset,)*2),
                                fill=(0, 0, 0, 0))
            
                image.alpha_composite(img)

            start_angle += angle

        return image


    