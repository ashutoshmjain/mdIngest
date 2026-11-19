from manim import *
import numpy as np

# COMPATIBILITY SHIMS FOR MANIM CE
# Constants & Easing
ease_in_out_sine = smooth
ease_in_sine = smooth
ease_out_sine = smooth
ease_out_expo = smooth
anticipate = smooth
bounce_it = smooth
acceleration = smooth
ease_in_back = smooth
ZERO = ORIGIN
START = ORIGIN

# GrowFromBottom shim (supports GrowFromBottom(mob))
def GrowFromBottom(mobject, **kwargs):
    return GrowFromEdge(mobject, DOWN, **kwargs)

# DashedRectangle shim
def DashedRectangle(*args, **kwargs):
    kwargs.pop('size', None)
    return Rectangle(*args, **kwargs)

# Safe Text shim (accepts size= as font_size=, and forces str(text))
_orig_Text = Text
def SafeText(text="", *args, **kwargs):
    if 'size' in kwargs and 'font_size' not in kwargs:
        kwargs['font_size'] = kwargs.pop('size')
    else:
        kwargs.pop('size', None)
    return _orig_Text(str(text), *args, **kwargs)
Text = SafeText

# Monkey patch Mobject.__init__ to ignore unexpected 'size'
_orig_Mobject_init = Mobject.__init__
def _safe_mobject_init(self, *args, **kwargs):
    kwargs.pop('size', None)
    _orig_Mobject_init(self, *args, **kwargs)
Mobject.__init__ = _safe_mobject_init

# Monkey patch Animation.__init__ to ignore unexpected args and log them
_orig_Animation_init = Animation.__init__
def _safe_anim_init(self, *args, **kwargs):
    # Strip common unsupported args
    for k in list(kwargs.keys()):
        if k in ['size', 'rate_func', 'scale_factor']:
            # print(f"DEBUG: Popping {k} from {type(self)}")
            kwargs.pop(k, None)
    _orig_Animation_init(self, *args, **kwargs)
Animation.__init__ = _safe_anim_init

# Wrap VMobject.scale
_orig_VMobject_scale = VMobject.scale
def _safe_scale(self, factor, **kwargs):
    kwargs.pop('scale_tips', None)
    return _orig_VMobject_scale(self, factor, **kwargs)
VMobject.scale = _safe_scale

# Monkey patch VMobject.set_fill so .set_fill(0.4) works as .set_fill(opacity=0.4)
_orig_set_fill = VMobject.set_fill
def _safe_set_fill(self, color=None, opacity=None, family=True):
    if isinstance(color, (int, float)) and opacity is None:
        return _orig_set_fill(self, color=None, opacity=float(color), family=family)
    return _orig_set_fill(self, color=color, opacity=opacity, family=family)
VMobject.set_fill = _safe_set_fill

# Add camera.frame shim to Camera for non-MovingCameraScene scenes
if not hasattr(Camera, "frame"):
    _dummy_camera_frame = Rectangle(width=8.0, height=8.0, stroke_opacity=0, fill_opacity=0)
    Camera.frame = property(lambda self: _dummy_camera_frame)

# Arrow & CurvedArrow shims
_orig_DoubleArrow = DoubleArrow
def DoubleArrow(*args, **kwargs):
    if "bend_angle" in kwargs:
        kwargs["path_arc"] = kwargs.pop("bend_angle")
    return _orig_DoubleArrow(*args, **kwargs)

_orig_CurvedDoubleArrow = CurvedDoubleArrow
def CurvedDoubleArrow(*args, **kwargs):
    if "bend_angle" in kwargs:
        kwargs["path_arc"] = kwargs.pop("bend_angle")
    return _orig_CurvedDoubleArrow(*args, **kwargs)

_orig_Arrow = Arrow
def Arrow(*args, **kwargs):
    if "bend_angle" in kwargs:
        kwargs["path_arc"] = kwargs.pop("bend_angle")
    if len(args) == 1 and isinstance(args[0], (list, tuple)) and len(args[0]) == 2:
        return _orig_Arrow(args[0][0], args[0][1], **kwargs)
    return _orig_Arrow(*args, **kwargs)

_orig_CurvedArrow = CurvedArrow
def SafeCurvedArrow(start_point, end_point, **kwargs):
    try:
        return _orig_CurvedArrow(start_point, end_point, **kwargs)
    except Exception:
        kwargs.pop("radius", None)
        return _orig_CurvedArrow(start_point, end_point, **kwargs)
CurvedArrow = SafeCurvedArrow

_orig_ArcBetweenPoints = ArcBetweenPoints
def SafeArcBetweenPoints(start, end, angle=TAU/4, radius=None, **kwargs):
    try:
        return _orig_ArcBetweenPoints(start, end, angle=angle, radius=radius, **kwargs)
    except Exception:
        try:
            return _orig_ArcBetweenPoints(start, end, angle=angle, radius=None, **kwargs)
        except Exception:
            return Line(start, end, color="#FFFFFF")
ArcBetweenPoints = SafeArcBetweenPoints

# Scene Helpers
def ShowCreationThenFadeOut(mob):
    return Succession(Create(mob), FadeOut(mob))

config.pixel_width = 740
config.pixel_height = 740
config.frame_width = 8.0
config.frame_height = 8.0
config.background_color = "#000000"

def get_footer_and_title(*args, **kwargs):
    cat_str = "KineticVector"
    str_args = [a for a in args if isinstance(a, str)]
    if len(str_args) >= 2:
        cat_str = str_args[1]
    elif len(str_args) == 1:
        cat_str = str_args[0]
    if "category_text" in kwargs or "category_str" in kwargs:
        cat_str = kwargs.get("category_text") or kwargs.get("category_str")
    if "archetype" in kwargs:
        cat_str = kwargs.get("archetype")

    # Archetype titles are permanently disabled to prevent visual distraction; return an empty VGroup for title
    title = VGroup()
    footer_line = Line(LEFT * 3.5, RIGHT * 3.5, color="#334155", stroke_width=1.5).move_to(DOWN * 3.35)
    footer_line.set_opacity(0.6)
    left_text = Text(cat_str, font="Arial", weight=NORMAL, font_size=10, color="#64748b").next_to(footer_line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    right_text = Text("deepDive podcast", font="Arial", weight=NORMAL, font_size=10, color="#64748b").next_to(footer_line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    return title, footer_line, left_text, right_text

def setup_base_scene(scene=None, *args, **kwargs):
    if scene and hasattr(scene, "add"):
        title, fline, ltext, rtext = get_footer_and_title(*args, **kwargs)
        scene.add(title, fline, ltext, rtext)

setup_scene_base = setup_base_scene

def get_footer(scene=None, category="KineticVector", *args, **kwargs):
    line = Line(LEFT * 3.5, RIGHT * 3.5, color="#334155", stroke_width=1.5).move_to(DOWN * 3.35)
    line.set_opacity(0.6)
    cat_text = category if isinstance(category, str) else "KineticVector"
    t_left = Text(cat_text, font="Arial", weight=NORMAL, font_size=10, color="#64748b").next_to(line, DOWN, buff=0.12).to_edge(LEFT, buff=0.55)
    t_right = Text("deepDive podcast", font="Arial", weight=NORMAL, font_size=10, color="#64748b").next_to(line, DOWN, buff=0.12).to_edge(RIGHT, buff=0.55)
    if scene and hasattr(scene, "add"):
        scene.add(line, t_left, t_right)
    return VGroup(line, t_left, t_right)

# Monkey patch VGroup & Mobject for missing methods
def _noop_method(self, *args, **kwargs):
    return self

for cls in (Mobject, VGroup, Rectangle):
    if not hasattr(cls, "shake"):
        cls.shake = _noop_method
    if not hasattr(cls, "make_allocatable"):
        cls.make_allocatable = _noop_method
