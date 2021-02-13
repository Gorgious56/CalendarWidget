from datetime import datetime, timedelta
import calendar

from bpy.types import (
    Panel,
    World,
    PropertyGroup,
    Operator,
)
from bpy.props import (
    IntProperty,
    PointerProperty,
)
from bpy.utils import (
    register_class,
    unregister_class,
)

bl_info = {
    "name": "Calendar Widget",
    "blender": (2, 80, 0),
    "category": "Tools",
    "location": "View 3D > UI (N Panel)",
    "version": (1, 0, 0),
    "author": "Gorgious56",
    "description": """Simple Panel that lets the user input a date/time""",
    "doc_url": "https://github.com/Gorgious56"
}


class CalendarProps(PropertyGroup):
    year: IntProperty(min=1, soft_min=1900, soft_max=2100,
                      max=9999, default=datetime.now().year)
    month: IntProperty(min=1, max=12, default=1)
    day: IntProperty(min=1, max=31)
    hour: IntProperty(min=0, max=23, default=datetime.now().hour)
    minute: IntProperty(min=0, max=59, default=datetime.now().minute)
    second: IntProperty(min=0, max=59, default=datetime.now().second)


class Calendar_OT_Change_Date(Operator):
    """Change date in the world properties"""
    bl_idname = "calendar.change_date"
    bl_label = "Change Date"
    bl_options = {'UNDO', 'INTERNAL'}

    year: IntProperty()
    month: IntProperty()
    day: IntProperty()
    hour: IntProperty()
    minute: IntProperty()
    second: IntProperty()

    def execute(self, context):
        props = context.scene.world.calendar_props
        if self.month > 12:
            self.year += 1
            self.month = 1
        elif self.month <= 0:
            self.year -= 1
            self.month = 12

        if self.day:
            props.day = self.day
        if self.month:
            props.month = self.month
        if self.year:
            props.year = self.year
        if self.hour:
            props.hour = self.hour
        if self.minute:
            props.minute = self.minute
        if self.second:
            props.second = self.second

        return {'FINISHED'}


class CalendarPanel(Panel):
    """Task Tracker Panel in the 3d View"""
    bl_idname = "CALENDAR_PANEL_PT_layout"
    bl_label = "Calendar Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Calendar'

    def draw(self, context):
        props = context.scene.world.calendar_props
        day = props.day
        month = props.month
        year = props.year
        now = datetime.now()

        layout = self.layout

        split = layout.split(factor=0.1)
        self.change_day_op(
            split,
            "",
            {
                "month": now.month,
                "year": now.year,
                "day": now.day,
                "hour": now.hour,
                "minute": now.minute,
                "second": now.second,
            },
            icon='RECOVER_LAST'
        )
        header = split.split(factor=0.7)

        row = header.row()
        row.label(text=calendar.month_name[month].upper())
        row.prop(props, "year", text="", emboss=False)

        row = header.row(align=True)
        for txt, inc in zip(("<", ">"), (-1, 1)):
            self.change_day_op(
                row, txt, {"month": month + inc, "year": year})

        date = datetime(year, month, 1)

        weekday = date.weekday()

        for r in range(7):
            new_date = None
            row = layout.row(align=True)
            for c in range(8):
                col = row.column(align=True)
                label = ""
                if c == 0:
                    if r == 0:
                        label = "#"
                    else:
                        label = "w" + \
                            str((date + timedelta(days=(r - 1) * 7)
                                 ).isocalendar()[1])
                elif r == 0:
                    label = calendar.day_name[c - 1][0:3].upper()
                else:
                    new_date = date + \
                        timedelta(days=c - 1 + (r - 1) * 7 - weekday)
                    label = new_date.day
                if isinstance(label, int) and new_date:
                    self.change_day_op(
                        col,
                        str(label),
                        {
                            "day": label,
                            "month": new_date.month,
                            "year": new_date.year,
                        },
                        emboss=new_date.month == month,
                        depress=(new_date.day == day
                                 and new_date.month == month
                                 and new_date.year == year))
                else:
                    col.label(text=str(label))
        layout.separator()
        row = layout.row()
        for p, t in zip(("hour", "minute", "second"), (":", "''", "'")):
            split = row.split(factor=0.8)
            split.prop(props, p, text="")
            split.label(text=t)

    @staticmethod
    def change_day_op(layout, txt, op_settings, emboss=True, depress=False, icon=None):
        if icon:
            op = layout.operator(Calendar_OT_Change_Date.bl_idname,
                                 text=txt, emboss=emboss, depress=depress, icon=icon)
        else:
            op = layout.operator(Calendar_OT_Change_Date.bl_idname,
                                 text=txt, emboss=emboss, depress=depress)

        for op_prop, op_value in op_settings.items():
            setattr(op, op_prop, op_value)


classes = (
    CalendarPanel,
    CalendarProps,

    Calendar_OT_Change_Date,
)


def register():
    for cls in classes:
        register_class(cls)
    World.calendar_props = PointerProperty(type=CalendarProps)


def unregister():
    del World.calendar_props
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
