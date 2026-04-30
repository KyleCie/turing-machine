"""
USE OF A.I. :
This program was made by Gemma 4, locally.
No A.I. on cloud was used.
"""


from .turingSystem import Turing, Transition
from turing_system.astSystem import Program

try:
    import pygame
except ImportError as e:
    raise e

import time

# ── Palette monochrome ─────────────────────────────────────────────────────────
BG           = (8,   8,   8)
FG           = (235, 235, 235)
DIM          = (90,  90,  90)
MID          = (155, 155, 155)
ACCENT       = (255, 255, 255)
HEAD_BG      = (42,  42,  42)
PANEL_BG     = (13,  13,  13)
PANEL_BORDER = (65,  65,  65)
SEL_BG       = (32,  32,  32)
ERROR_COL    = (210, 90,  90)

CELL_W       = 72
CELL_H       = 72
CELL_MARGIN  = 6
WRITE_FX_DUR = 10

SPEED_PRESETS = (0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 60.0)


# ── Helpers pour accéder aux commandes d'un état ──────────────────────────────

def _get_commands(state_obj) -> dict:
    """
    Retourne le dict de transitions d'un état.
    Format attendu : { valeur_lue: ('val_écrite', 'état_suivant', 'left'|'right')
                                  | 'STOP' }
    Tente plusieurs noms d'attributs courants.
    """
    if isinstance(state_obj, dict):
        return state_obj
    for attr in ("commands", "transitions", "rules", "table",
                 "_commands", "_transitions"):
        val = getattr(state_obj, attr, None)
        if isinstance(val, dict):
            return val
    return {}


def _set_commands(state_obj, commands: dict) -> bool:
    """Réécrit le dict de transitions. Retourne True si l'attribut existait."""
    if isinstance(state_obj, dict):
        state_obj.clear()
        state_obj.update(commands)
        return True
    for attr in ("commands", "transitions", "rules", "table",
                 "_commands", "_transitions"):
        if hasattr(state_obj, attr):
            setattr(state_obj, attr, commands)
            return True
    return False


def _fmt_cmd(val_seen: str, action) -> str:
    """Formate une entrée du dict en ligne texte lisible."""
    # Transition dataclass
    if hasattr(action, 'stop'):
        if action.stop:
            return f"{val_seen}, STOP"
        return f"{val_seen}, {action.write}, {action.next_state}, {action.direction}"
    # fallback legacy
    if action == "STOP" or (isinstance(action, str) and action.upper() == "STOP"):
        return f"{val_seen}, STOP"
    if isinstance(action, (tuple, list)) and len(action) == 3:
        w, ns, d = action
        return f"{val_seen}, {w}, {ns}, {d}"
    return f"{val_seen}, {action}"


def _parse_cmd(line: str, known_states: set) -> tuple:
    """
    Parse une ligne de commande.
    Retourne (val_seen, action, erreur_str).
    action est soit 'STOP' soit (write_val, next_state, direction).
    Si erreur_str != '', l'action est None.
    """
    parts = [p.strip() for p in line.split(",")]
    if len(parts) == 2:
        val_seen, action = parts
        if action.upper() != "STOP":
            return None, None, "Format : val, STOP"
        return val_seen, "STOP", ""
    if len(parts) == 4:
        val_seen, write_val, next_state, direction = parts
        if direction.lower() not in ("left", "right"):
            return None, None, "Direction : 'left' ou 'right'"
        if next_state not in known_states:
            return None, None, f"État inconnu : '{next_state}'"
        return val_seen, (write_val, next_state, direction.lower()), ""
    return None, None, "Format : val, STOP  |  val, écriture, état, gauche|droite"


# ─────────────────────────────────────────────────────────────────────────────

class GraphicTuring:

    def __init__(self, program: Program) -> None:
        self.program = program
        self.turing  = Turing(program)

        # ── animation bande ────────────────────────────────────────────────
        self._tape_offset_x: float   = 0.0
        self._target_offset_x: float = 0.0
        self._write_fx: int          = 0
        self._written_idx: int | None = None

        # ── vitesse — time-based, sans arrondi de frame ────────────────────
        self._auto_run: bool        = False
        self._speed_idx: int        = 2          # 1.0 pas/s par défaut
        self._last_step_time: float = 0.0        # time.monotonic()

        # ── stats ──────────────────────────────────────────────────────────
        self._step_count: int = 0

        # ── éditeur ───────────────────────────────────────────────────────
        self._edit_mode: bool           = False
        self._edit_sel_state: str | None = None
        self._edit_sel_line: int        = -1
        self._edit_active: bool         = False  # saisie de texte en cours
        self._edit_text: str            = ""
        self._edit_cursor: int          = 0
        self._edit_error: str           = ""
        self._edit_state_scroll: int    = 0
        self._edit_cmd_scroll: int      = 0
        # rects construits à chaque frame par _draw_editor
        self._edit_state_rects: dict    = {}
        self._edit_cmd_rects: dict      = {}
        self._edit_activate_rect: pygame.Rect | None = None

    # ── propriétés vitesse ─────────────────────────────────────────────────

    @property
    def _steps_per_sec(self) -> float:
        return SPEED_PRESETS[self._speed_idx]

    @property
    def _step_interval(self) -> float:
        return 1.0 / self._steps_per_sec

    # ── cellules visibles ──────────────────────────────────────────────────

    def _visible_cells(self, screen_w: int) -> list:
        tape = self.turing.tape
        if tape is None:
            return []
        head_idx = tape.get_index()
        n_side   = (screen_w // (CELL_W + CELL_MARGIN)) // 2 + 2
        half     = screen_w // 2

        # rewind à gauche
        node = tape.get_chain()
        node_idx = head_idx
        for _ in range(n_side + 5):
            left = node.get_left()
            if left is None:
                break
            node = left
            node_idx -= 1

        cells = []
        while node is not None:
            rel = node_idx - head_idx
            if rel > n_side + 2:
                break
            px = half + rel * (CELL_W + CELL_MARGIN) + int(self._tape_offset_x)
            cells.append((node_idx, node, px))
            node = node.get_right()
            node_idx += 1
        return cells

    # ── rendu bande ────────────────────────────────────────────────────────

    def _draw_background(self, surface: pygame.Surface) -> None:
        surface.fill(BG)
        w, h = surface.get_size()
        for x in range(0, w, 48):
            pygame.draw.line(surface, (14, 14, 14), (x, 0), (x, h))
        for y in range(0, h, 48):
            pygame.draw.line(surface, (14, 14, 14), (0, y), (w, y))

    def _draw_tape(self, surface: pygame.Surface,
                   font_big: pygame.font.Font,
                   font_small: pygame.font.Font) -> None:
        w, h = surface.get_size()
        if self.turing.tape is None:
            return

        head_idx = self.turing.tape.get_index()
        cy       = h // 2 - 20
        cells    = self._visible_cells(w)

        for (idx, chain, px) in cells:
            is_head    = idx == head_idx
            is_written = idx == self._written_idx and self._write_fx > 0
            dist       = abs(idx - head_idx)

            if is_head:
                bg_col, bd_col, bd_w = HEAD_BG, ACCENT, 2
            elif is_written:
                t      = self._write_fx / WRITE_FX_DUR
                lum    = int(200 * t)
                bg_col = (lum // 5, lum // 5, lum // 5)
                bd_col = (lum, lum, lum)
                bd_w   = 2
            else:
                alpha  = max(0.0, 1.0 - dist / 9.0)
                lum    = int(alpha * 50)
                bg_col = (lum // 3, lum // 3, lum // 3)
                bd_col = (max(18, lum), max(18, lum), max(18, lum))
                bd_w   = 1

            rect = pygame.Rect(px - CELL_W // 2, cy - CELL_H // 2, CELL_W, CELL_H)
            pygame.draw.rect(surface, bg_col, rect, border_radius=4)
            pygame.draw.rect(surface, bd_col, rect, bd_w, border_radius=4)

            val     = chain.get_value()
            alpha   = max(0.18, 1.0 - dist / 8.0)
            txt_col = ACCENT if is_head else tuple(int(c * alpha) for c in FG)
            ts      = font_big.render(val, True, txt_col)
            surface.blit(ts, ts.get_rect(center=(px, cy)))

            is_col = MID if is_head else DIM
            is_s   = font_small.render(str(idx), True, is_col)
            surface.blit(is_s, is_s.get_rect(center=(px, cy + CELL_H // 2 + 14)))

        # triangle tête de lecture
        hx  = w // 2
        pts = [(hx, cy - CELL_H // 2 - 6),
               (hx - 9, cy - CELL_H // 2 - 20),
               (hx + 9, cy - CELL_H // 2 - 20)]
        pygame.draw.polygon(surface, ACCENT, pts)

        # règle
        pygame.draw.line(surface, PANEL_BORDER,
                         (0, cy + CELL_H // 2 + 28),
                         (w, cy + CELL_H // 2 + 28), 1)

    # ── panneau d'information gauche ───────────────────────────────────────

    def _draw_panel(self, surface: pygame.Surface,
                    font_title: pygame.font.Font,
                    font_body: pygame.font.Font,
                    font_small: pygame.font.Font) -> None:
        w, h = surface.get_size()
        pw, ph = 290, h - 80
        px, py = 40, 40
        m  = 16

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((*PANEL_BG, 220))
        surface.blit(panel, (px, py))
        pygame.draw.rect(surface, PANEL_BORDER,
                         pygame.Rect(px, py, pw, ph), 1, border_radius=2)

        y = py + m

        def row(label: str, value: str, vcol=FG):
            nonlocal y
            ls = font_small.render(label, True, DIM)
            surface.blit(ls, (px + m, y));  y += ls.get_height() + 2
            vs = font_body.render(value, True, vcol)
            surface.blit(vs, (px + m, y));  y += vs.get_height() + 12

        t = font_title.render("TURING MACHINE", True, ACCENT)
        surface.blit(t, (px + m, y));  y += t.get_height() + 4
        pygame.draw.line(surface, PANEL_BORDER,
                         (px + m, y), (px + pw - m, y), 1);  y += 12

        row("ÉTAT", self.turing.name_state or "—",
            vcol=(MID if not self.turing.end else DIM))
        row("ÉTAPE", str(self._step_count))
        if self.turing.tape:
            row("INDEX TÊTE", str(self.turing.tape.get_index()), MID)

        ls = font_small.render("ALPHABET", True, DIM)
        surface.blit(ls, (px + m, y));  y += ls.get_height() + 4
        vals = "  ".join(self.turing.values) if self.turing.values else "—"
        vs   = font_small.render(vals, True, MID)
        surface.blit(vs, (px + m, y));  y += vs.get_height() + 12

        ls = font_small.render("ÉTATS", True, DIM)
        surface.blit(ls, (px + m, y));  y += ls.get_height() + 4
        for sn in self.turing.states:
            is_cur = sn == self.turing.name_state
            col    = ACCENT if is_cur else MID
            prefix = "> " if is_cur else "  "
            ss = font_small.render(f"{prefix}{sn}", True, col)
            surface.blit(ss, (px + m, y));  y += ss.get_height() + 2
            if y > py + ph - m - 50:
                break

        # statut bas du panneau
        if self.turing.end:
            st, sc = "ARRÊT", DIM
        elif self._auto_run:
            st, sc = f"AUTO  {self._steps_per_sec:.3g} pas/s", ACCENT
        elif self._edit_mode:
            st, sc = "ÉDITEUR", MID
        else:
            st, sc = "PAUSE", FG
        ss = font_body.render(st, True, sc)
        surface.blit(ss, (px + m, py + ph - ss.get_height() - m))

    # ── barre de contrôles bas ─────────────────────────────────────────────

    def _draw_controls(self, surface: pygame.Surface,
                       font_ctrl: pygame.font.Font) -> None:
        w, h = surface.get_size()
        bar_h = 42
        bar = pygame.Surface((w, bar_h), pygame.SRCALPHA)
        bar.fill((5, 5, 5, 240))
        surface.blit(bar, (0, h - bar_h))
        pygame.draw.line(surface, PANEL_BORDER, (0, h - bar_h), (w, h - bar_h), 1)

        speed_str = (f"{int(self._steps_per_sec)} pas/s"
                     if self._steps_per_sec >= 1
                     else f"1/{int(1/self._steps_per_sec)} pas/s")

        controls = [
            ("ESPACE",  "Pas à pas"),
            ("ENTRÉE",  "Auto / Pause"),
            ("↑ ↓",     speed_str),
            ("E",       "Éditeur" if not self._edit_mode else "Fermer édit."),
            ("R",       "Reset"),
            ("ÉCHAP",   "Quitter"),
        ]

        items = []
        for key, desc in controls:
            ks = font_ctrl.render(f" {key} ", True, BG)
            bg = pygame.Surface((ks.get_width() + 4, ks.get_height() + 4))
            bg.fill(FG)
            bg.blit(ks, (2, 2))
            ds = font_ctrl.render(f" {desc}", True, MID)
            items.append((bg, ds))

        gap     = 18
        total_w = sum(k.get_width() + d.get_width() for k, d in items) + gap * (len(items) - 1)
        x       = (w - total_w) // 2
        cy      = h - bar_h // 2
        for bg, ds in items:
            surface.blit(bg, (x, cy - bg.get_height() // 2))
            x += bg.get_width()
            surface.blit(ds, (x, cy - ds.get_height() // 2))
            x += ds.get_width() + gap

    # ── éditeur ───────────────────────────────────────────────────────────

    def _state_lines(self, state_name: str) -> list[str]:
        """Lignes texte des commandes d'un état."""
        if state_name not in self.turing.states:
            return []
        cmds = _get_commands(self.turing.states[state_name])
        return [_fmt_cmd(k, v) for k, v in cmds.items()]

    def _apply_edit(self) -> str:
        """
        Valide et applique la ligne en cours d'édition.
        Retourne "" si ok, message d'erreur sinon.
        """
        sn = self._edit_sel_state
        li = self._edit_sel_line
        if sn is None or li < 0:
            return "Aucune ligne sélectionnée"

        state_obj = self.turing.states.get(sn)
        if state_obj is None:
            return "État introuvable"

        cmds     = _get_commands(state_obj)
        old_keys = list(cmds.keys())
        if li >= len(old_keys):
            return "Index hors limites"

        val_seen_old = old_keys[li]
        val_seen_new, action, err = _parse_cmd(
            self._edit_text, set(self.turing.states.keys())
        )
        if err:
            return err

        # Convertit en Transition
        if action == "STOP":
            transition = Transition(stop=True)
        else:
            w, ns, d = action
            transition = Transition(write=w, next_state=ns, direction=d, stop=False)

        new_cmds = {}
        for k, v in cmds.items():
            new_cmds[val_seen_new if k == val_seen_old else k] = (
                transition if k == val_seen_old else v
            )

        if not _set_commands(state_obj, new_cmds):
            return "Impossible d'écrire dans l'objet State (attribut inconnu)"

        return ""

    def _draw_editor(self, surface: pygame.Surface,
                     font_title: pygame.font.Font,
                     font_body: pygame.font.Font,
                     font_small: pygame.font.Font,
                     font_mono: pygame.font.Font) -> None:
        w, h = surface.get_size()

        # voile
        ov = pygame.Surface((w, h), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 200))
        surface.blit(ov, (0, 0))

        # fenêtre
        ew, eh = w - 140, h - 110
        ex, ey = 70, 55
        pygame.draw.rect(surface, PANEL_BG,     (ex, ey, ew, eh), border_radius=4)
        pygame.draw.rect(surface, PANEL_BORDER, (ex, ey, ew, eh), 1, border_radius=4)

        m  = 20
        y  = ey + m

        # titre
        t = font_title.render("ÉDITEUR D'ÉTATS", True, ACCENT)
        surface.blit(t, (ex + m, y));  y += t.get_height() + 6
        pygame.draw.line(surface, PANEL_BORDER,
                         (ex + m, y), (ex + ew - m, y), 1);  y += 12

        body_h  = font_body.get_height()
        line_h  = body_h + 7
        col_w   = 230                         # largeur colonne états
        lx      = ex + m                      # x col. gauche
        rx      = lx + col_w + 24             # x col. droite
        rw      = ew - col_w - m * 3 - 24    # largeur col. droite
        bottom  = ey + eh - 70               # limite basse pour les listes

        # ── colonne gauche : liste des états ──────────────────────────────
        self._edit_state_rects = {}
        lbl = font_small.render("ÉTATS", True, DIM)
        surface.blit(lbl, (lx, y))
        ry = y + lbl.get_height() + 6

        state_names = list(self.turing.states.keys())
        for i, sn in enumerate(state_names[self._edit_state_scroll:],
                                self._edit_state_scroll):
            if ry + line_h > bottom - line_h * 2:
                break
            is_sel = sn == self._edit_sel_state
            is_cur = sn == self.turing.name_state

            r = pygame.Rect(lx - 4, ry - 2, col_w, line_h)
            if is_sel:
                pygame.draw.rect(surface, SEL_BG, r, border_radius=2)
                pygame.draw.rect(surface, PANEL_BORDER, r, 1, border_radius=2)

            col    = ACCENT if is_cur else (FG if is_sel else MID)
            prefix = "> " if is_cur else "  "
            ss     = font_body.render(f"{prefix}{sn}", True, col)
            surface.blit(ss, (lx, ry))
            self._edit_state_rects[sn] = r
            ry += line_h

        # bouton "Activer comme état courant"
        self._edit_activate_rect = None
        if (self._edit_sel_state
                and self._edit_sel_state != self.turing.name_state
                and not self.turing.end):
            btn_lbl = f"[ Activer '{self._edit_sel_state}' ]"
            bs  = font_small.render(btn_lbl, True, FG)
            br  = bs.get_rect(topleft=(lx, ry + 8))
            brx = br.inflate(10, 6)
            pygame.draw.rect(surface, SEL_BG, brx, border_radius=2)
            pygame.draw.rect(surface, PANEL_BORDER, brx, 1, border_radius=2)
            surface.blit(bs, br)
            self._edit_activate_rect = brx

        # ── colonne droite : commandes de l'état sélectionné ─────────────
        self._edit_cmd_rects = {}
        sel_label = self._edit_sel_state or "(sélectionner un état à gauche)"
        lbl2 = font_small.render(f"COMMANDES — {sel_label}", True, DIM)
        surface.blit(lbl2, (rx, y))
        cy2 = y + lbl2.get_height() + 6

        if self._edit_sel_state:
            lines = self._state_lines(self._edit_sel_state)
            for i, line in enumerate(lines[self._edit_cmd_scroll:],
                                      self._edit_cmd_scroll):
                if cy2 + line_h > bottom:
                    break
                is_sel_line = i == self._edit_sel_line
                r = pygame.Rect(rx - 4, cy2 - 2, rw, line_h)
                if is_sel_line:
                    pygame.draw.rect(surface, SEL_BG, r, border_radius=2)
                    pygame.draw.rect(surface, PANEL_BORDER, r, 1, border_radius=2)

                if is_sel_line and self._edit_active:
                    # zone de saisie avec curseur clignotant
                    before = self._edit_text[:self._edit_cursor]
                    after  = self._edit_text[self._edit_cursor:]
                    bs_s   = font_mono.render(before, True, FG)
                    surface.blit(bs_s, (rx, cy2))
                    cx = rx + bs_s.get_width()
                    if int(time.monotonic() * 2) % 2 == 0:
                        pygame.draw.line(surface, ACCENT,
                                         (cx, cy2 + 2),
                                         (cx, cy2 + font_mono.get_height() - 2), 2)
                    as_s = font_mono.render(after, True, FG)
                    surface.blit(as_s, (cx, cy2))
                else:
                    col  = FG if is_sel_line else MID
                    ls   = font_mono.render(line, True, col)
                    surface.blit(ls, (rx, cy2))

                self._edit_cmd_rects[i] = r
                cy2 += line_h

        # ── message d'erreur ──────────────────────────────────────────────
        if self._edit_error:
            es = font_small.render(f"⚠  {self._edit_error}", True, ERROR_COL)
            surface.blit(es, (rx, ey + eh - 58))

        # ── aide contextuelle ─────────────────────────────────────────────
        hint_lines = [
            "CLIC : sélectionner    ENTRÉE : éditer / valider    ÉCHAP : annuler / fermer éditeur",
            "Format commande :   val, STOP     |     val, valeur_écrite, état_cible, left|right",
        ]
        for i, hl in enumerate(hint_lines):
            hs = font_small.render(hl, True, DIM)
            surface.blit(hs, (ex + m, ey + eh - 38 + i * 18))

    # ── logique ────────────────────────────────────────────────────────────

    def _step(self) -> None:
        if self.turing.end or self.turing.tape is None:
            return
        prev_idx = self.turing.tape.get_index()
        self.turing.run()
        new_idx  = self.turing.tape.get_index()

        delta = new_idx - prev_idx
        self._tape_offset_x  += delta * (CELL_W + CELL_MARGIN)
        self._target_offset_x = 0.0
        self._written_idx     = prev_idx
        self._write_fx        = WRITE_FX_DUR
        self._step_count     += 1
        self._last_step_time  = time.monotonic()

    def _reset(self) -> None:
        self.turing           = Turing(self.program)
        self._tape_offset_x   = 0.0
        self._target_offset_x = 0.0
        self._write_fx        = 0
        self._written_idx     = None
        self._auto_run        = False
        self._step_count      = 0
        self._last_step_time  = time.monotonic()
        self._edit_mode       = False
        self._edit_sel_state  = None
        self._edit_sel_line   = -1
        self._edit_active     = False
        self._edit_text       = ""
        self._edit_error      = ""

    # ── gestion éditeur ────────────────────────────────────────────────────

    def _editor_click(self, pos: tuple) -> None:
        mx, my = pos

        for sn, r in self._edit_state_rects.items():
            if r.collidepoint(mx, my):
                if sn != self._edit_sel_state:
                    self._edit_sel_state  = sn
                    self._edit_sel_line   = -1
                    self._edit_active     = False
                    self._edit_cmd_scroll = 0
                self._edit_error = ""
                return

        if self._edit_activate_rect and self._edit_activate_rect.collidepoint(mx, my):
            self.turing.name_state = self._edit_sel_state
            return

        for i, r in self._edit_cmd_rects.items():
            if r.collidepoint(mx, my):
                if self._edit_active and self._edit_sel_line == i:
                    self._commit_edit()
                else:
                    self._edit_sel_line = i
                    self._edit_active   = False
                    self._edit_error    = ""
                return

    def _start_edit(self) -> None:
        if self._edit_sel_state is None or self._edit_sel_line < 0:
            return
        lines = self._state_lines(self._edit_sel_state)
        if self._edit_sel_line < len(lines):
            self._edit_text   = lines[self._edit_sel_line]
            self._edit_cursor = len(self._edit_text)
            self._edit_active = True
            self._edit_error  = ""

    def _commit_edit(self) -> None:
        err = self._apply_edit()
        if err:
            self._edit_error = err
        else:
            self._edit_active = False
            self._edit_error  = ""

    def _editor_key(self, event: pygame.event.Event) -> bool:
        """Retourne True si la touche a été consommée par l'éditeur."""

        if not self._edit_active:
            if event.key == pygame.K_RETURN and self._edit_sel_line >= 0:
                self._start_edit()
                return True
            if event.key == pygame.K_ESCAPE:
                if self._edit_active:
                    self._edit_active = False
                elif self._edit_sel_state:
                    self._edit_sel_state = None
                    self._edit_sel_line  = -1
                else:
                    self._edit_mode = False
                return True
            return False

        # saisie active
        if event.key == pygame.K_RETURN:
            self._commit_edit()
        elif event.key == pygame.K_ESCAPE:
            self._edit_active = False
            self._edit_error  = ""
        elif event.key == pygame.K_BACKSPACE:
            if self._edit_cursor > 0:
                t = self._edit_text
                self._edit_text   = t[:self._edit_cursor - 1] + t[self._edit_cursor:]
                self._edit_cursor -= 1
        elif event.key == pygame.K_DELETE:
            if self._edit_cursor < len(self._edit_text):
                t = self._edit_text
                self._edit_text = t[:self._edit_cursor] + t[self._edit_cursor + 1:]
        elif event.key == pygame.K_LEFT:
            self._edit_cursor = max(0, self._edit_cursor - 1)
        elif event.key == pygame.K_RIGHT:
            self._edit_cursor = min(len(self._edit_text), self._edit_cursor + 1)
        elif event.key == pygame.K_HOME:
            self._edit_cursor = 0
        elif event.key == pygame.K_END:
            self._edit_cursor = len(self._edit_text)
        elif event.unicode and event.unicode.isprintable():
            t = self._edit_text
            self._edit_text   = t[:self._edit_cursor] + event.unicode + t[self._edit_cursor:]
            self._edit_cursor += 1
        return True

    # ── boucle principale ──────────────────────────────────────────────────

    def run(self) -> None:
        pygame.init()
        pygame.display.set_caption("Turing Machine")
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        W, H   = screen.get_size()
        clock  = pygame.time.Clock()

        mono = ("couriernew"
                if pygame.font.match_font("couriernew")
                else "monospace")

        font_title = pygame.font.SysFont(mono, 19, bold=True)
        font_body  = pygame.font.SysFont(mono, 25, bold=True)
        font_big   = pygame.font.SysFont(mono, 30, bold=True)
        font_small = pygame.font.SysFont(mono, 16)
        font_ctrl  = pygame.font.SysFont(mono, 15, bold=True)
        font_mono  = pygame.font.SysFont(mono, 18)

        self._last_step_time = time.monotonic()
        running = True

        while running:
            now = time.monotonic()

            # ── événements ────────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self._edit_mode:
                        self._editor_click(event.pos)

                elif event.type == pygame.KEYDOWN:

                    # l'éditeur a la priorité sur les touches globales
                    if self._edit_mode:
                        consumed = self._editor_key(event)
                        if consumed:
                            continue

                    if event.key == pygame.K_ESCAPE:
                        if self._edit_mode:
                            self._edit_mode = False
                        else:
                            running = False

                    elif event.key == pygame.K_SPACE:
                        if not self.turing.end:
                            self._auto_run = False
                            self._step()

                    elif event.key == pygame.K_RETURN:
                        if not self.turing.end:
                            self._auto_run = not self._auto_run
                            self._last_step_time = now

                    elif event.key == pygame.K_r:
                        self._reset()

                    elif event.key == pygame.K_e:
                        # E ouvre/ferme l'éditeur (uniquement en pause)
                        if not self._auto_run:
                            self._edit_mode  = not self._edit_mode
                            self._edit_active = False
                            self._edit_error  = ""

                    elif event.key == pygame.K_UP:
                        self._speed_idx = min(len(SPEED_PRESETS) - 1,
                                              self._speed_idx + 1)

                    elif event.key == pygame.K_DOWN:
                        self._speed_idx = max(0, self._speed_idx - 1)

            # ── auto-run (time-based, aucun arrondi de frame) ─────────────
            if self._auto_run and not self.turing.end and not self._edit_mode:
                if now - self._last_step_time >= self._step_interval:
                    self._step()
                    if self.turing.end:
                        self._auto_run = False

            # ── interpolation déplacement bande ───────────────────────────
            diff = self._target_offset_x - self._tape_offset_x
            if abs(diff) < 0.5:
                self._tape_offset_x = self._target_offset_x
            else:
                self._tape_offset_x += diff * 0.20

            if self._write_fx > 0:
                self._write_fx -= 1

            # ── rendu ─────────────────────────────────────────────────────
            self._draw_background(screen)
            self._draw_tape(screen, font_big, font_small)
            self._draw_panel(screen, font_title, font_body, font_small)
            self._draw_controls(screen, font_ctrl)

            if self._edit_mode:
                self._draw_editor(screen, font_title, font_body,
                                  font_small, font_mono)

            # bannière HALT
            if self.turing.end:
                hf  = pygame.font.SysFont(mono, 42, bold=True)
                txt = hf.render("MACHINE ARRÊTÉE", True, FG)
                gl  = pygame.Surface(
                    (txt.get_width() + 60, txt.get_height() + 28),
                    pygame.SRCALPHA)
                gl.fill((255, 255, 255, 10))
                cr  = txt.get_rect(center=(W // 2, H // 2 + 140))
                screen.blit(gl, cr.move(-30, -14))
                screen.blit(txt, cr)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()