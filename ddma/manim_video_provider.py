import os
import av
from PIL import Image

MODULE_03_MANIM_SCENES = [
    {"num": 1, "start": 835.0, "end": 865.0, "title": "PERISHABLE INVENTORY // ARROW OF TIME"},
    {"num": 2, "start": 865.0, "end": 893.8, "title": "THE DIGITAL JAR FALLACY"},
    {"num": 3, "start": 893.8, "end": 922.5, "title": "PERISHABLE ASSET VS UTILITY"},
    {"num": 4, "start": 922.5, "end": 952.5, "title": "GEOGRAPHIC MONOPOLY VS SPOT MARKET"},
    {"num": 5, "start": 952.5, "end": 983.8, "title": "ZERO BRAND LOYALTY // GLADIATOR ARENA"},
    {"num": 6, "start": 983.8, "end": 1013.6, "title": "ALGORITHMIC YIELD MANAGEMENT"},
    {"num": 7, "start": 1013.6, "end": 1042.0, "title": "THE $1.50 BLUNT INSTRUMENT"},
    {"num": 8, "start": 1042.0, "end": 1072.0, "title": "CONTINUOUS YIELD OPTIMIZATION"},
    {"num": 9, "start": 1072.0, "end": 1101.9, "title": "PEAK SURGE & MIDNIGHT CITY"},
    {"num": 10, "start": 1101.9, "end": 1131.0, "title": "MARGINAL COST FLOOR // CLUB HYPERION"},
    {"num": 11, "start": 1131.0, "end": 1161.0, "title": "TIER 1: HIGH-SPEED TRADING BOTS"},
    {"num": 12, "start": 1161.0, "end": 1190.0, "title": "TIER 3: STANDBY BATCH FORKLIFT"},
    {"num": 13, "start": 1190.0, "end": 1220.0, "title": "DISEMBODIED INTELLIGENCE KEYS"},
    {"num": 14, "start": 1220.0, "end": 1248.6, "title": "WEIGHTS MATRIX & EMPTY IT DESK"},
    {"num": 15, "start": 1248.6, "end": 1278.0, "title": "MCP & THE CYBER BOUNCER"},
    {"num": 16, "start": 1278.0, "end": 1307.0, "title": "HANDING CONTROLS TO AI GATEWAY"},
    {"num": 17, "start": 1307.0, "end": 1336.5, "title": "OPERATIONAL SOVEREIGNTY OUROBOROS"},
    {"num": 18, "start": 1336.5, "end": 1354.0, "title": "HOMEOSTATIC GOVERNANCE"},
]

MODULE_04_MANIM_SCENES = [
    {"num": 1, "start": 1353.5, "end": 1383.5, "title": "PASSIVE CODE // SOVEREIGN ADMINISTRATOR"},
    {"num": 2, "start": 1383.5, "end": 1411.6, "title": "ASTRONOMICAL CAPEX // SUNK R&D COSTS"},
    {"num": 3, "start": 1411.6, "end": 1441.3, "title": "BORN IN DEBT // THE SPV ENTITY"},
    {"num": 4, "start": 1441.3, "end": 1470.2, "title": "KINETIC 1 // 3-TRANCHE CASHFLOW WATERFALL"},
    {"num": 5, "start": 1470.2, "end": 1501.3, "title": "TRANCHE 1 // SHEER SURVIVAL LIFE SUPPORT"},
    {"num": 6, "start": 1501.3, "end": 1531.6, "title": "TRANCHE 2 & 3 // AMORTIZATION TO TREASURY"},
    {"num": 7, "start": 1531.6, "end": 1559.9, "title": "CORPORATE DE-RISKING // TOLL ROAD MODEL"},
    {"num": 8, "start": 1559.9, "end": 1589.4, "title": "THE BRICK WALL // TRADITIONAL BANKS HANG UP"},
    {"num": 9, "start": 1589.4, "end": 1619.4, "title": "LEGAL INCOMPATIBILITY // PASSPORTS & HEARTBEATS"},
    {"num": 10, "start": 1619.4, "end": 1648.7, "title": "PAYMENT RAILS // BATCH CLEARING FRICTION"},
    {"num": 11, "start": 1648.7, "end": 1678.9, "title": "DYNAMIC SLIDE // THE $0.30 FEE IMPLOSION"},
    {"num": 12, "start": 1678.9, "end": 1708.6, "title": "SUPER DUMB ANALOGY // $10 GRAIN OF RICE"},
    {"num": 13, "start": 1708.6, "end": 1738.7, "title": "FOUNDATIONAL CODE // 1997 WEB PROTOCOLS"},
    {"num": 14, "start": 1738.7, "end": 1769.2, "title": "HTTP 402 // PAYMENT REQUIRED (DORMANT)"},
    {"num": 15, "start": 1769.2, "end": 1797.3, "title": "L402 PROTOCOL // LIGHTNING OPERATIONALIZED"},
    {"num": 16, "start": 1797.3, "end": 1826.9, "title": "SPEED OF LIGHT // BASE CHAIN VS LAYER 2"},
    {"num": 17, "start": 1826.9, "end": 1857.2, "title": "STATELESS LOCAL VERIFICATION // NO CENTRAL DB"},
    {"num": 18, "start": 1857.2, "end": 1887.7, "title": "KINETIC 2 // SHA-256 ONE-WAY SCRAMBLER"},
    {"num": 19, "start": 1887.7, "end": 1917.6, "title": "CRYPTOGRAPHIC WAX SEAL // MACAROON PROOF"},
    {"num": 20, "start": 1917.6, "end": 1931.5, "title": "SELF-CONTAINED VERIFICATION // UNLOCKED"},
]

class ManimSceneReader:
    def __init__(self, scenes_config=None, rendered_dir=None, fps=25, start_seconds=None):
        if scenes_config:
            self.scenes = scenes_config
            self.rendered_dir = rendered_dir or "scratch/manim_module_03/rendered"
        elif start_seconds is not None and start_seconds >= 1350.0:
            self.scenes = MODULE_04_MANIM_SCENES
            self.rendered_dir = rendered_dir or "scratch/manim_module_04/rendered"
        else:
            self.scenes = MODULE_03_MANIM_SCENES
            self.rendered_dir = rendered_dir or "scratch/manim_module_03/rendered"
        self.fps = fps
        self.current_num = None
        self.container = None
        self.stream = None
        self.last_img = None
        self.cur_frame_idx = -1

    def get_scene_for_time(self, t):
        for sc in self.scenes:
            if sc["start"] <= t < sc["end"]:
                return sc
        if self.scenes:
            if t >= self.scenes[-1]["end"]:
                return self.scenes[-1]
            return self.scenes[0]
        return None

    def get_frame(self, t):
        active_sc = self.get_scene_for_time(t)
        if not active_sc:
            return self.last_img or Image.new("RGB", (1920, 860), (8, 12, 20))

        num = active_sc["num"]
        if num != self.current_num:
            if self.container:
                try:
                    self.container.close()
                except Exception:
                    pass
            self.current_num = num
            path = os.path.join(self.rendered_dir, f"scene_{num:02d}.mp4")
            if os.path.exists(path):
                try:
                    self.container = av.open(path)
                    self.stream = self.container.streams.video[0]
                    self.cur_frame_idx = -1
                except Exception as e:
                    print(f"Error opening {path}: {e}")
                    self.container = None
                    self.stream = None
            else:
                self.container = None
                self.stream = None

        if not self.container:
            return self.last_img or Image.new("RGB", (1920, 860), (8, 12, 20))

        local_t = max(0.0, t - active_sc["start"])
        target_f_idx = int(round(local_t * self.fps))

        if target_f_idx == self.cur_frame_idx and self.last_img is not None:
            return self.last_img

        try:
            if target_f_idx < self.cur_frame_idx:
                self.container.seek(0)
                self.cur_frame_idx = -1

            for frame in self.container.decode(self.stream):
                self.cur_frame_idx += 1
                if self.cur_frame_idx >= target_f_idx:
                    self.last_img = frame.to_image()
                    return self.last_img
        except Exception:
            pass

        return self.last_img or Image.new("RGB", (1920, 860), (8, 12, 20))

    def close(self):
        if self.container:
            try:
                self.container.close()
            except Exception:
                pass
            self.container = None
