(() => {
  "use strict";

  // The initial seal plane. Each dot is a separate projected cell.
  const rows = [
    "          #########            ",
    "          #       #            ",
    "          # o ### #            ",
    "          #   # # #            ",
    "          # # # # ####         ",
    "          # # #      #         ",
    "          # # ###### #         ",
    "          # #        #         ",
    "          # # ###### #         ",
    "    ####### # #      #         ",
    "    #       # ###### ##########",
    "    # # # # # # #             #",
    "##### # # # # # # ######### o #",
    "#     # # #   ###             #",
    "# ### # # ####   ###### ##### #",
    "# #   # # #  #   #  # # #   # #",
    "# ##### ######   #### # # ### #",
    "#             ###   # # #     #",
    "# o ######### # # # # # # #####",
    "#             # # # # # # #    ",
    "########## ###### #       #    ",
    "         #      # # #######    ",
    "         # ###### # #          ",
    "         #        # #          ",
    "         # ###### # #          ",
    "         #      # # #          ",
    "         #### # # # #          ",
    "            # # #   #          ",
    "            # ### o #          ",
    "            #       #          ",
    "            #########          "
  ];

  const FULL_TURN = 2 * Math.PI;
  const TURN_MS = 1400;
  const INK = 1;
  const DOT = 512;
  const DIRECTIONS = {
    "1,0": 2, "0,1": 4, "-1,0": 8, "0,-1": 16,
    "1,1": 32, "-1,1": 64, "-1,-1": 128, "1,-1": 256,
  };
  const FACE_GLYPHS = "·╺╻┏╸━┓┳╹┗┃┣┛┻┫╋";
  const EDGE_GLYPHS = "·╶╷┌╴─┐┬╵└│├┘┴┤┼";

  function prepareTurn({ rows }) {
    const height = rows.length;
    const width = rows[0]?.length;
    if (!width || rows.some(row => row.length !== width || /[^ #o]/u.test(row))) {
      throw new TypeError("Expected a rectangular grid containing spaces, # and o.");
    }

    const points = [];
    const byCell = new Map();
    const strokes = [];
    const inkAt = (x, y) => rows[y]?.[x] === "#";

    rows.forEach((row, y) => {
      Array.from(row).forEach((cell, x) => {
        if (cell === " ") return;
        byCell.set(y * width + x, points.length);
        points.push({
          x, y,
          dot: cell === "o",
          leftEdge: cell === "#" && !inkAt(x - 1, y),
          rightEdge: cell === "#" && !inkAt(x + 1, y),
        });
      });
    });

    points.forEach(({ x, y, dot }, from) => {
      if (dot) return;
      for (const [dx, dy] of [[1, 0], [0, 1], [1, 1], [-1, 1]]) {
        if (!inkAt(x + dx, y + dy)) continue;
        // Skip the diagonal across a corner that already has a cardinal path.
        if (dx && dy && (inkAt(x + dx, y) || inkAt(x, y + dy))) continue;
        strokes.push([from, byCell.get((y + dy) * width + x + dx)]);
      }
    });

    return { width, height, points, strokes };
  }

  function connect(grid, width, [x, y], [nextX, nextY]) {
    const dx = nextX - x;
    const dy = nextY - y;
    // Adjacent source cells can stay adjacent or project onto the same cell.
    if (!dx && !dy) return;
    grid[y * width + x] |= INK | DIRECTIONS[`${dx},${dy}`];
    grid[nextY * width + nextX] |= INK | DIRECTIONS[`${-dx},${-dy}`];
  }

  function glyph(mask, box) {
    if (mask & DOT) return "▪";
    const cardinal = (mask >> 1) & 15;
    const falling = mask & (32 | 128);
    const rising = mask & (64 | 256);

    if (!falling && !rising) return box[cardinal];
    if (cardinal & 5 && cardinal & 10) return box[cardinal];
    if (cardinal & 5) return box[5];
    if (cardinal & 10) return box[10];
    if (falling && rising) return "╳";
    return falling ? "╲" : "╱";
  }

  function renderFrame({ width, height, points, strokes }, yaw) {
    const cos = Math.cos(yaw);
    const sin = Math.sin(yaw);
    const center = (width - 1) / 2;
    const halfDepth = Math.min(2.5, (width - 1) * 0.065);
    const faceRadius = center * Math.abs(cos);
    const depthRadius = halfDepth * Math.abs(sin);
    const radius = faceRadius + depthRadius;
    const fit = radius > center ? center / radius : 1;
    const nearZ = cos >= 0 ? halfDepth : -halfDepth;
    const farCenter = center - fit * nearZ * sin;
    // Match the weights at edge-on. The rear rail lightens from its outer
    // columns inward as the face opens and the projected core shrinks.
    const heavyRailRadius = fit * Math.max(0, depthRadius - faceRadius);
    // The dots cross through the thickness, keeping them in view at edge-on.
    const dotZ = faceRadius < depthRadius ? nearZ * (faceRadius / depthRadius) : nearZ;

    // Rotate around the vertical axis, then project orthographically onto the grid.
    // The face toward the camera covers the exposed side rails wherever they meet.
    const project = ({ x, y }, z) =>
      [Math.round(center + fit * ((x - center) * cos + z * sin)), y];
    const near = points.map(point => project(point, nearZ));
    const far = points.map(point => project(point, -nearZ));
    const side = sin >= 0 ? "leftEdge" : "rightEdge";
    const face = new Uint16Array(width * height);
    const rails = new Uint16Array(face.length);
    const walls = new Uint8Array(face.length);

    points.forEach((point, index) => {
      const [x, y] = point.dot ? project(point, dotZ) : near[index];
      face[y * width + x] |= point.dot ? DOT : INK;
      if (!point[side]) return;
      const [farX] = far[index];
      if (x === farX) return;
      rails[y * width + farX] |= INK;
      walls.fill(1, y * width + Math.min(x, farX), y * width + Math.max(x, farX) + 1);
    });

    for (const [from, to] of strokes) {
      connect(face, width, near[from], near[to]);
      if (points[from][side] && points[to][side]) {
        connect(rails, width, far[from], far[to]);
      }
    }

    const rows = [];
    for (let y = 0; y < height; y++) {
      let row = "";
      for (let x = 0; x < width; x++) {
        const cell = y * width + x;
        if (face[cell]) {
          row += glyph(face[cell], FACE_GLYPHS);
        } else if (rails[cell]) {
          const railBox = Math.abs(x - farCenter) < heavyRailRadius ? FACE_GLYPHS : EDGE_GLYPHS;
          row += glyph(rails[cell], railBox);
        } else {
          row += walls[cell] ? "┄" : " ";
        }
      }
      rows.push(row);
    }
    return rows;
  }

  function angleAt(progress) {
    if (progress <= 0) return 0;
    if (progress >= 1) return FULL_TURN;
    const eased = (1 - Math.cos(Math.PI * progress)) / 2;
    // A small linear share gets past the first cell sooner at both ends.
    return FULL_TURN * (0.85 * eased + 0.15 * progress);
  }

  function enhance(art, mesh) {
    const motion = window.matchMedia("(prefers-reduced-motion: no-preference)");
    const rowElements = Array.from(art.querySelectorAll(".footer-mark__row"));
    const front = rowElements.map(row => row.textContent);
    const button = document.createElement("button");
    button.type = "button";
    button.className = "footer-mark__button";
    button.setAttribute("aria-label", "Rotate calligraphy mark");

    let frameId = null;
    let startTime = null;
    let pressedTouch = null;

    function clearTouchPress() {
      pressedTouch = null;
      button.removeAttribute("data-touch-pressed");
    }

    function endTouchPress(event) {
      if (event.pointerId === pressedTouch) clearTouchPress();
    }

    function paint(frame) {
      rowElements.forEach((row, index) => {
        if (row.textContent !== frame[index]) row.textContent = frame[index];
      });
    }

    function restore() {
      if (frameId !== null) window.cancelAnimationFrame(frameId);
      frameId = null;
      startTime = null;
      paint(front);
    }

    function tick(time) {
      if (!motion.matches) {
        syncPreference();
        return;
      }
      startTime ??= time;
      const angle = angleAt((time - startTime) / TURN_MS);
      if (angle === FULL_TURN) {
        restore();
        return;
      }

      if (angle > 0) paint(renderFrame(mesh, angle));
      frameId = window.requestAnimationFrame(tick);
    }

    function syncPreference() {
      if (!motion.matches) {
        clearTouchPress();
        restore();
        if (art.parentNode === button) {
          button.replaceWith(art);
          art.removeAttribute("aria-hidden");
        }
      } else if (art.parentNode !== button) {
        art.setAttribute("aria-hidden", "true");
        art.replaceWith(button);
        button.append(art);
      }
    }

    // Touch browsers may delay :active until click. Show the press on contact
    // while leaving the browser to decide whether the gesture becomes a click.
    button.addEventListener("pointerdown", event => {
      if (event.pointerType === "touch" && event.isPrimary && motion.matches) {
        pressedTouch = event.pointerId;
        button.setAttribute("data-touch-pressed", "");
      }
    });
    for (const type of ["pointerup", "pointercancel", "lostpointercapture"]) {
      button.addEventListener(type, endTouchPress);
    }

    button.addEventListener("click", () => {
      if (motion.matches && frameId === null) frameId = window.requestAnimationFrame(tick);
    });

    // A held Enter key should trigger only its first native click.
    button.addEventListener("keydown", event => {
      if (event.key === "Enter" && event.repeat) event.preventDefault();
    });

    motion.addEventListener("change", syncPreference);
    syncPreference();
  }

  const marks = document.querySelectorAll("[data-footer-mark-art]");
  if (marks.length > 0) {
    const mesh = prepareTurn({ rows });
    for (const art of marks) enhance(art, mesh);
  }
})();
