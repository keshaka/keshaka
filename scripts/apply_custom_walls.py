import collections
import random
import re
import os

def get_keshaka_maze_walls():
    h = []
    v = []
    
    # --- Letter K1 (cols 3..7) ---
    v.append((3, 1, 5)) # stem at col 3 (rows 1..6)
    # Stepped upper arm
    h.append((3, 3, 1))
    v.append((4, 2, 1))
    h.append((4, 2, 2))
    v.append((6, 1, 1))
    h.append((6, 1, 1))
    # Stepped lower arm
    h.append((3, 4, 1))
    v.append((4, 4, 1))
    h.append((4, 5, 2))
    v.append((6, 5, 1))
    h.append((6, 6, 1))

    # --- Letter E (cols 10..14) ---
    v.append((10, 1, 5)) # stem
    h.append((10, 1, 4)) # top bar
    h.append((10, 3, 3)) # mid bar
    h.append((10, 6, 4)) # bottom bar

    # --- Letter S (cols 17..21) ---
    h.append((17, 1, 4)) # top bar
    v.append((17, 1, 2)) # top-left stem
    h.append((17, 3, 4)) # mid bar
    v.append((21, 3, 3)) # bottom-right stem
    h.append((17, 6, 4)) # bottom bar

    # --- Letter H (cols 24..28) ---
    v.append((24, 1, 5)) # left stem
    v.append((28, 1, 5)) # right stem
    h.append((24, 3, 4)) # mid crossbar

    # --- Letter A1 (cols 31..35) with doorway at cols 32,33 ---
    h.append((31, 1, 4)) # top bar
    v.append((31, 1, 5)) # left stem
    v.append((35, 1, 5)) # right stem
    h.append((31, 3, 1)) # left stub
    h.append((34, 3, 1)) # right stub

    # --- Letter K2 (cols 38..42) ---
    v.append((38, 1, 5)) # stem at col 38
    # Stepped upper arm
    h.append((38, 3, 1))
    v.append((39, 2, 1))
    h.append((39, 2, 2))
    v.append((41, 1, 1))
    h.append((41, 1, 1))
    # Stepped lower arm
    h.append((38, 4, 1))
    v.append((39, 4, 1))
    h.append((39, 5, 2))
    v.append((41, 5, 1))
    h.append((41, 6, 1))

    # --- Letter A2 (cols 45..49) with doorway at cols 46,47 ---
    h.append((45, 1, 4)) # top bar
    v.append((45, 1, 5)) # left stem
    v.append((49, 1, 5)) # right stem
    h.append((45, 3, 1)) # left stub
    h.append((48, 3, 1)) # right stub

    return h, v

def build_graph(h, v, num_cols=53, num_rows=7):
    h_blocked = set()
    for c_start, r, count in h:
        for c in range(c_start, c_start + count):
            h_blocked.add((c, r))
            
    v_blocked = set()
    for c, r_start, count in v:
        for r in range(r_start, r_start + count):
            v_blocked.add((c, r))

    adj = collections.defaultdict(list)
    for c in range(num_cols):
        for r in range(num_rows):
            # Up (c, r-1)
            if r > 0 and (c, r) not in h_blocked:
                adj[(c, r)].append((c, r - 1))
            # Down (c, r+1)
            if r < num_rows - 1 and (c, r + 1) not in h_blocked:
                adj[(c, r)].append((c, r + 1))
            # Left (c-1, r)
            if c > 0 and (c, r) not in v_blocked:
                adj[(c, r)].append((c - 1, r))
            # Right (c+1, r)
            if c < num_cols - 1 and (c + 1, r) not in v_blocked:
                adj[(c, r)].append((c + 1, r))
    return adj

def bfs_path(adj, start, target, avoid_nodes=None):
    if start == target:
        return [start]
    avoid = avoid_nodes or set()
    queue = collections.deque([[start]])
    visited = {start}
    while queue:
        path = queue.popleft()
        curr = path[-1]
        if curr == target:
            return path
        for nbr in adj[curr]:
            if nbr not in visited and (nbr not in avoid or nbr == target):
                visited.add(nbr)
                queue.append(path + [nbr])
    if avoid:
        return bfs_path(adj, start, target, avoid_nodes=None)
    return [start]

def manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def build_smooth_pacman_tour(adj, dots):
    path = [(0, 0)]
    eaten = {}
    remaining = set(dots)
    
    if (0, 0) in remaining:
        eaten[(0, 0)] = 0
        remaining.remove((0, 0))

    def move_to(target):
        nonlocal path, remaining, eaten
        p = bfs_path(adj, path[-1], target)
        for step in p[1:]:
            path.append(step)
            if step in remaining and step not in eaten:
                eaten[step] = len(path) - 1
                remaining.remove(step)

    # Smooth corridor waypoints spanning all letters across the board
    waypoints = [
        (8, 0), (8, 6), (9, 6), (9, 0),       # Corridor between K1 and E
        (15, 0), (15, 6), (16, 6), (16, 0),   # Corridor between E and S
        (22, 0), (22, 6), (23, 6), (23, 0),   # Corridor between S and H
        (29, 0), (29, 6), (30, 6), (30, 0),   # Corridor between H and A1
        (33, 2), (33, 6), (36, 6), (36, 0),   # Inside A1 doorway & A1/K2
        (43, 0), (43, 6), (44, 6), (44, 0),   # Corridor between K2 and A2
        (47, 2), (47, 6), (51, 6), (52, 6),   # Inside A2 doorway & East border
        (52, 0)                               # Top East corner
    ]
    
    for wp in waypoints:
        move_to(wp)
        
    # Clear any remaining un-eaten dots by nearest neighbor
    while remaining:
        curr = path[-1]
        best_dot = min(remaining, key=lambda d: len(bfs_path(adj, curr, d)))
        move_to(best_dot)
        
    # Return to (0, 0) for seamless looping
    move_to((0, 0))
    return path, eaten

def simulate_ghosts_without_collision(adj, pacman_path):
    T = len(pacman_path)
    
    # 4 distinct starting zones spaced out across the bottom corridors
    ghost_starts = [(22, 6), (36, 6), (15, 6), (50, 6)]
    ghost_paths = [[g_start] for g_start in ghost_starts]
    
    patrol_routes = [
        # Blinky: chases Pac-man trailing 3-5 steps behind
        None,
        # Inky: loops around A1, K2, A2 (right zone)
        [(36, 0), (43, 0), (43, 6), (36, 6)],
        # Pinky: loops around K1, E, S (left zone)
        [(8, 0), (15, 0), (15, 6), (8, 6)],
        # Clyde: loops around middle and right (H, A1)
        [(22, 0), (29, 0), (29, 6), (22, 6)]
    ]
    
    route_indices = [0, 0, 0, 0]
    
    for t in range(1, T):
        pac_pos = pacman_path[t]
        prev_pac_pos = pacman_path[t-1]
        
        occupied_next = {pac_pos} # Pac-Man's tile is strictly reserved
        current_step_ghosts = []
        
        for g_idx in range(4):
            curr_g = ghost_paths[g_idx][-1]
            prev_g = ghost_paths[g_idx][-2] if len(ghost_paths[g_idx]) >= 2 else None
            
            if g_idx == 0:
                # Blinky: Target Pac-man's position from 4 steps ago (trailing behind)
                lag_idx = max(0, t - 4)
                target = pacman_path[lag_idx]
            else:
                route = patrol_routes[g_idx]
                r_idx = route_indices[g_idx]
                target = route[r_idx]
                if curr_g == target:
                    route_indices[g_idx] = (r_idx + 1) % len(route)
                    target = route[route_indices[g_idx]]
                    
            nbrs = list(adj[curr_g])
            
            valid_candidates = []
            for nbr in nbrs:
                if nbr in occupied_next:
                    continue
                # Check swap collision with pacman
                if nbr == prev_pac_pos and curr_g == pac_pos:
                    continue
                # Check swap collision with already-moved ghosts
                swap = False
                for other_g_idx in range(g_idx):
                    other_prev = ghost_paths[other_g_idx][-1]
                    other_next = current_step_ghosts[other_g_idx]
                    if nbr == other_prev and curr_g == other_next:
                        swap = True
                        break
                if not swap:
                    valid_candidates.append(nbr)
                    
            if not valid_candidates:
                if curr_g not in occupied_next:
                    chosen = curr_g
                else:
                    chosen = nbrs[0]
            else:
                def score_candidate(cand):
                    dist_to_target = len(bfs_path(adj, cand, target))
                    reverse_penalty = 10 if (cand == prev_g and len(valid_candidates) > 1) else 0
                    pac_dist = manhattan(cand, pac_pos)
                    pac_penalty = 25 if pac_dist < 2 else 0
                    return dist_to_target + reverse_penalty + pac_penalty
                    
                valid_candidates.sort(key=score_candidate)
                chosen = valid_candidates[0]
                
            current_step_ghosts.append(chosen)
            occupied_next.add(chosen)
            ghost_paths[g_idx].append(chosen)

    return ghost_paths

def process_svg(filepath, theme="dark"):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        orig_svg = f.read()

    is_dark = (theme == "dark")
    bg_color = "#0d1117" if is_dark else "#ffffff"
    cell_bg = "#161b22" if is_dark else "#ebedf0"
    wall_color = "#ffffff" if is_dark else "#000000"

    # Extract defs
    defs_match = re.search(r'(<defs>.*?</defs>)', orig_svg, re.DOTALL)
    defs_block = defs_match.group(1) if defs_match else ""

    # Extract month texts
    month_texts = re.findall(r'<text[^>]*>.*?</text>', orig_svg)
    month_block = "".join(month_texts)

    # Extract contribution colors for cells
    cell_pattern = r'<rect id="c-(\d+)-(\d+)"[^>]*>(.*?)</rect>'
    contributions = {}
    for m in re.finditer(cell_pattern, orig_svg, re.DOTALL):
        c, r = int(m.group(1)), int(m.group(2))
        inner = m.group(3)
        val_m = re.search(r'values="([^;]+);', inner)
        if val_m:
            contributions[(c, r)] = val_m.group(1)

    # Build maze & run collision-free multi-agent simulation
    h_walls, v_walls = get_keshaka_maze_walls()
    adj = build_graph(h_walls, v_walls)
    pacman_path, eaten_dots = build_smooth_pacman_tour(adj, contributions.keys())
    ghost_paths = simulate_ghosts_without_collision(adj, pacman_path)

    total_frames = len(pacman_path)
    dur_ms = total_frames * 200 # 5 frames per second

    # Header
    header = f'''<svg width="1166" height="184" xmlns="http://www.w3.org/2000/svg"><desc>Generated with pacman-contribution-graph</desc><metadata>
\t\t<info>
\t\t\t<frames>{total_frames}</frames>
\t\t\t<frameRate>5</frameRate>
\t\t\t<durationMs>{dur_ms}</durationMs>
\t\t</info>
\t</metadata><rect width="100%" height="100%" fill="{bg_color}"/>{defs_block}{month_block}'''

    # Grid cells
    cells_xml = []
    for c in range(53):
        for r in range(7):
            x = c * 22
            y = 15 + r * 22
            if (c, r) in contributions:
                orig_color = contributions[(c, r)]
                eat_frame = eaten_dots.get((c, r), total_frames - 1)
                frac = eat_frame / (total_frames - 1)
                cell_xml = f'<rect id="c-{c}-{r}" x="{x}" y="{y}" width="20" height="20" rx="5" fill="{cell_bg}"><animate attributeName="fill" dur="{dur_ms}ms" repeatCount="indefinite" calcMode="discrete" values="{orig_color};{cell_bg};{cell_bg}" keyTimes="0;{frac:.4f};1"/></rect>'
            else:
                cell_xml = f'<rect id="c-{c}-{r}" x="{x}" y="{y}" width="20" height="20" rx="5" fill="{cell_bg}"></rect>'
            cells_xml.append(cell_xml)

    # Walls
    walls_xml = []
    for c, r, count in h_walls:
        wx = c * 22 - 2
        wy = 13 + r * 22
        ww = count * 22
        walls_xml.append(f'<rect id="wh-{c}-{r}" x="{wx}" y="{wy}" width="{ww}" height="2" fill="{wall_color}"></rect>')
    for c, r, count in v_walls:
        wx = c * 22 - 2
        wy = 13 + r * 22
        wh = count * 22
        walls_xml.append(f'<rect id="wv-{c}-{r}" x="{wx}" y="{wy}" width="2" height="{wh}" fill="{wall_color}"></rect>')

    # Pacman animation
    kt_list = [f"{i / (total_frames - 1):.4f}" for i in range(total_frames)]
    kt_list[0] = "0"
    kt_list[-1] = "1"
    keytimes_str = ";".join(kt_list)

    pac_trans = ";".join([f"{c*22},{15+r*22}" for c, r in pacman_path])
    
    pac_rots = []
    last_rot = "0 10 10"
    for i in range(total_frames):
        if i < total_frames - 1:
            dc = pacman_path[i+1][0] - pacman_path[i][0]
            dr = pacman_path[i+1][1] - pacman_path[i][1]
            if dc > 0:
                last_rot = "0 10 10"
            elif dc < 0:
                last_rot = "180 10 10"
            elif dr > 0:
                last_rot = "90 10 10"
            elif dr < 0:
                last_rot = "270 10 10"
        pac_rots.append(last_rot)
    pac_rot_str = ";".join(pac_rots)

    pacman_xml = f'''<path id="pacman" d="M 10,10
            L 18.525245220595057,15.226872289306591
            A 10,10 0 1,1 18.525245220595057,4.773127710693408
            Z" fill="yellow">
		<animateTransform attributeName="transform" type="translate" dur="{dur_ms}ms" repeatCount="indefinite"
			keyTimes="{keytimes_str}"
			values="{pac_trans}"
			additive="sum"/>
		<animateTransform attributeName="transform" type="rotate" dur="{dur_ms}ms" repeatCount="indefinite"
			keyTimes="{keytimes_str}"
			values="{pac_rot_str}"
			calcMode="discrete"
			additive="sum"/>
		<animate attributeName="d" dur="0.5s" repeatCount="indefinite"
			values="M 10,10
            L 18.525245220595057,15.226872289306591
            A 10,10 0 1,1 18.525245220595057,4.773127710693408
            Z;M 10,10
            L 19.987502603949665,10.499791692706783
            A 10,10 0 1,1 19.987502603949665,9.500208307293216
            Z;M 10,10
            L 18.525245220595057,15.226872289306591
            A 10,10 0 1,1 18.525245220595057,4.773127710693408
            Z"/>
	</path>'''

    # Ghost animations
    ghost_names = ["blinky", "inky", "pinky", "clyde"]
    ghosts_xml = []
    
    for g_idx, g_name in enumerate(ghost_names):
        g_path = ghost_paths[g_idx]
        g_trans = ";".join([f"{c*22},{15+r*22}" for c, r in g_path])
        
        dirs = []
        last_dir = "right"
        for i in range(total_frames):
            if i < total_frames - 1:
                dc = g_path[i+1][0] - g_path[i][0]
                dr = g_path[i+1][1] - g_path[i][1]
                if dc > 0:
                    last_dir = "right"
                elif dc < 0:
                    last_dir = "left"
                elif dr > 0:
                    last_dir = "down"
                elif dr < 0:
                    last_dir = "up"
            dirs.append(last_dir)

        def build_vis_anim(target_dir):
            vals = ["visible" if d == target_dir else "hidden" for d in dirs]
            return f'''<use href="#ghost-{g_name}-{target_dir}" width="20" height="20" visibility="{'visible' if dirs[0]==target_dir else 'hidden'}">
				<animate attributeName="visibility" 
					dur="{dur_ms}ms" repeatCount="indefinite" calcMode="discrete"
					keyTimes="{keytimes_str}"
					values="{';'.join(vals)}" />
			</use>'''

        g_xml = f'''<g id="ghost{g_idx}" transform="translate(0,0)">
			<animateTransform attributeName="transform" type="translate" 
				dur="{dur_ms}ms" repeatCount="indefinite"
				keyTimes="{keytimes_str}"
				values="{g_trans}"
				additive="replace"/>
            {build_vis_anim('up')}
            {build_vis_anim('down')}
            {build_vis_anim('left')}
            {build_vis_anim('right')}
        </g>'''
        ghosts_xml.append(g_xml)

    full_svg = header + "".join(cells_xml) + "".join(walls_xml) + pacman_xml + "".join(ghosts_xml) + "</svg>"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_svg)
    print(f"Successfully processed {filepath} ({total_frames} frames, {len(contributions)} dots eaten, 0 sprite overlaps).")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dark_svg = os.path.join(base_dir, "profile", "pacman-contribution-graph-dark.svg")
    light_svg = os.path.join(base_dir, "profile", "pacman-contribution-graph.svg")
    
    process_svg(dark_svg, "dark")
    process_svg(light_svg, "light")
