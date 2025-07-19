from typing import List, Dict, Any
from collections import defaultdict
from markdown_utils import create_anchor_label, convert_mentions_in_html, replace_mentions, md_escape
import re

def paginate_and_columnize(lines, lines_per_page=55):
    pages = []
    current = []
    for line in lines:
        current.append(line)
        if len(current) == lines_per_page:
            pages.append(current)
            current = []
    if current:
        pages.append(current)
    # Now, for each page, split into two columns
    result = []
    for page in pages:
        col_break = lines_per_page // 2
        col1 = page[:col_break]
        col2 = page[col_break:]
        # Remove trailing empty lines in each column
        while col1 and col1[-1].strip() == '':
            col1.pop()
        while col2 and col2[-1].strip() == '':
            col2.pop()
        result.append('\n'.join(col1) + '\n/\n' + '\n'.join(col2))
    return result

def generate_worldbook(locations: Dict[int, Dict[str, Any]], characters: List[Dict[str, Any]], charlocations: Dict[int, Dict[str, Any]], organizations: List[Dict[str, Any]], events: List[Dict[str, Any]], entity_map: Dict[int, Dict[str, str]], character_id_to_entity_id: Dict[int, int], notes: List[Dict[str, Any]], items: List[Dict[str, Any]], families: List[Dict[str, Any]], races: List[Dict[str, Any]], include_private=False) -> str:
    import re
    from collections import defaultdict
    from markdown_utils import create_anchor_label, convert_mentions_in_html, replace_mentions, md_escape

    # Splits a list of markdown lines into "visual blocks" for pagination/columnization.
    # It joins the lines into a single string, then splits at points that look like the start of a new
    # paragraph, header, list item, or other major markdown/HTML block element.
    # This helps keep related content together when paginating or splitting into columns.
    def split_visual_blocks(section_lines):
        text = '\n'.join(section_lines)
        # Split at the start of HTML block tags or markdown headers/lists
        blocks = re.split(
            r'(?=<p|<hr|<div|<h[1-6]|<li|^#|^\* |^- |^\d+\. )',
            text,
            flags=re.MULTILINE
        )
        # Remove empty blocks and strip whitespace
        blocks = [b.strip() for b in blocks if b.strip()]
        return blocks

    def add_section(section_lines, output_lines):
        blocks = split_visual_blocks(section_lines)
        lines_per_page = 80  # number of actual lines per page (increased from 35)
        min_blocks_for_page = 5  # reduced from 10
        min_blocks_for_column = 3  # reduced from 6

        # Helper: is this block a section header?
        # (moved import re to the top of the file)

        def is_section_header(block):
            block = block.lstrip()
            # Match markdown headers (#, ##, ###, etc.) or HTML headers (<h1>, <h2>, ..., <h6>)
            return (
                re.match(r'^#{1,6} ', block) is not None or
                re.match(r'^<h[1-6][ >]', block, re.IGNORECASE) is not None
            )

        # Count actual lines in a block
        def count_lines_in_block(block):
            return len(block.split('\n'))

        # Remove section headers from the end of a list of blocks, returning both trimmed blocks and removed headers
        def trim_trailing_section_headers(blocks):
            trimmed = list(blocks)
            removed = []
            while trimmed and is_section_header(trimmed[-1]):
                removed.insert(0, trimmed[-1])  # insert at start to preserve order
                trimmed.pop()
            #if removed:
                #print(f"[DEBUG] trim_trailing_section_headers called. Removed section headers: {removed}")
            return trimmed, removed

        pages = []
        current = []
        current_line_count = 0
        i = 0
        while i < len(blocks):
            block = blocks[i]
            block_line_count = count_lines_in_block(block)
            
            # If adding this block would exceed the page limit, check for a subsection in the next 4 blocks
            if current_line_count + block_line_count > lines_per_page and current:
                lookahead = 1
                found_subsection = False
                while lookahead <= 4 and (i + lookahead) < len(blocks):
                    next_block = blocks[i + lookahead].lstrip()
                    if next_block.startswith('## ') or next_block.startswith('<h2'):
                        # Add the subsection and its content to current page
                        for j in range(lookahead):
                            current.append(blocks[i + j])
                            current_line_count += count_lines_in_block(blocks[i + j])
                        i += lookahead
                        found_subsection = True
                        break
                    lookahead += 1
                
                # Only break the page if it has enough content
                if len(current) < min_blocks_for_page and pages:
                    # Merge with previous page
                    pages[-1].extend(current)
                else:
                    pages.append(list(current))
                current = []
                current_line_count = 0
            
            # Add the current block
            current.append(block)
            current_line_count += block_line_count
            i += 1
            
        if current:
            if len(current) < min_blocks_for_page and pages:
                pages[-1].extend(current)
            else:
                pages.append(list(current))
                
        # After building pages, merge any page that starts with a section header and is very short
        merged_pages = []
        for page in pages:
            if (
                merged_pages
                and page
                and is_section_header(page[0])
                and len(page) < min_blocks_for_page
            ):
                # Merge with previous page
                merged_pages[-1].extend(page)
            else:
                merged_pages.append(page)
        pages = merged_pages
        
        # Move trailing section headers from end of each page to start of next page
        for idx in range(len(pages) - 1):
            trimmed, removed = trim_trailing_section_headers(pages[idx])
            pages[idx] = trimmed
            if removed:
                # Always move section headers to the start of the next page, never leave at end of previous
                # Remove any duplicate headers at the start of the next page
                while pages[idx + 1] and is_section_header(pages[idx + 1][0]) and pages[idx + 1][0].strip() in [h.strip() for h in removed]:
                    pages[idx + 1].pop(0)
                pages[idx + 1] = removed + pages[idx + 1]
        # Last page: keep any trailing headers
        last_trimmed, last_removed = trim_trailing_section_headers(pages[-1])
        pages[-1] = last_trimmed + last_removed

        # Output pages/columns
        for idx, page in enumerate(pages):
            if len(page) < min_blocks_for_column * 2:
                # Not enough for two columns, output as single column
                if output_lines and (idx > 0 or len(output_lines) > 0):
                    output_lines.append('=')
                output_lines.append('\n'.join(page))
            else:
                mid = len(page) // 2
                col1 = page[:mid]
                col2 = page[mid:]
                # Move trailing section headers from col1 to start of col2
                col1_trimmed, col1_removed = trim_trailing_section_headers(col1)
                # Remove any duplicate headers at the start of col2
                while col2 and is_section_header(col2[0]) and col2[0].strip() in [h.strip() for h in col1_removed]:
                    col2.pop(0)
                col2 = col1_removed + col2
                # Move trailing section headers from col2 to end of col2 (since no next column)
                col2_trimmed, col2_removed = trim_trailing_section_headers(col2)
                col2 = col2_trimmed + col2_removed
                if output_lines and (idx > 0 or len(output_lines) > 0):
                    output_lines.append('=')
                output_lines.append('\n'.join(col1_trimmed))
                output_lines.append('|')
                output_lines.append('\n'.join(col2))

    # Helper to check privacy
    def is_private_obj(obj):
        ent = obj.get('entity', {})
        return obj.get('is_private', 0) == 1 or ent.get('is_private', 0) == 1

    # Debug: print counts before privacy filtering
    # print(f"[DEBUG] Locations before privacy filter: {len(locations)}")
    # print(f"[DEBUG] Characters before privacy filter: {len(characters)}")
    # print(f"[DEBUG] Charlocations before privacy filter: {len(charlocations)}")
    # print(f"[DEBUG] Organizations before privacy filter: {len(organizations)}")
    # print(f"[DEBUG] Events before privacy filter: {len(events)}")
    # print(f"[DEBUG] Items before privacy filter: {len(items)}")
    # print(f"[DEBUG] Families before privacy filter: {len(families)}")
    # print(f"[DEBUG] Notes before privacy filter: {len(notes)}")
    # print(f"[DEBUG] Races before privacy filter: {len(races)}")

    if not include_private:
        locations = {k: v for k, v in locations.items() if not is_private_obj(v)}
        characters = [c for c in characters if not is_private_obj(c)]
        charlocations = {k: v for k, v in charlocations.items() if not is_private_obj(v)}
        organizations = [o for o in organizations if not is_private_obj(o)]
        events = [e for e in events if not is_private_obj(e)]
        items = [i for i in items if not is_private_obj(i)]
        families = [f for f in families if not is_private_obj(f)]
        notes = [n for n in notes if not is_private_obj(n)]
        races = [r for r in races if not is_private_obj(r)]

    # print(f"[DEBUG] Locations after privacy filter: {len(locations)}")
    # print(f"[DEBUG] Characters after privacy filter: {len(characters)}")
    # print(f"[DEBUG] Charlocations after privacy filter: {len(charlocations)}")
    # print(f"[DEBUG] Organizations after privacy filter: {len(organizations)}")
    # print(f"[DEBUG] Events after privacy filter: {len(events)}")
    # print(f"[DEBUG] Items after privacy filter: {len(items)}")
    # print(f"[DEBUG] Families after privacy filter: {len(families)}")
    # print(f"[DEBUG] Notes after privacy filter: {len(notes)}")
    # print(f"[DEBUG] Races after privacy filter: {len(races)}")

    # Build location trees properly using location IDs (not entity IDs)
    # Convert the locations dict to use location IDs as keys instead of entity IDs
    location_by_id = {}
    for loc in locations.values():
        # Use the location's own ID, not the entity ID
        location_by_id[loc['id']] = loc
    
    charlocations_by_id = {loc['id']: loc for loc in charlocations.values()}
    
    # Build a complete location hierarchy using a tree structure
    # This approach can handle missing intermediate nodes and build the full hierarchy
    class LocationNode:
        def __init__(self, location_data):
            self.location = location_data
            self.children = []
            self.parent = None
            self.depth = 0
        
        def add_child(self, child_node):
            child_node.parent = self
            child_node.depth = self.depth + 1
            self.children.append(child_node)
        
        def get_name(self):
            return self.location.get('name') or self.location.get('entity', {}).get('name', 'Unnamed Location')
        
        def get_id(self):
            return self.location['id']
    
    # Create all location nodes
    location_nodes = {}
    for loc in locations.values():
        location_nodes[loc['id']] = LocationNode(loc)
    
    # Build parent-child relationships
    root_nodes = []
    for loc_id, node in location_nodes.items():
        parent_loc_id = node.location.get('location_id')
        if parent_loc_id and parent_loc_id in location_nodes:
            # This location has a parent that exists in our data
            parent_node = location_nodes[parent_loc_id]
            parent_node.add_child(node)
        else:
            # This is a root location (no parent or parent not in data)
            root_nodes.append(node)
    
    # Debug: Check for Tomasberg specifically
    tomasberg_found = False
    for loc in locations.values():
        if loc.get('name') == 'Tomasberg':
            tomasberg_found = True
            # print(f"[DEBUG] Found Tomasberg: id={loc['id']}, location_id={loc.get('location_id')}")
            parent_loc_id = loc.get('location_id')
            if parent_loc_id in location_by_id:
                # print(f"[DEBUG] Tomasberg parent found: {location_by_id[parent_loc_id].get('name')}")
                pass
            else:
                # print(f"[DEBUG] Tomasberg parent NOT found: {parent_loc_id}")
                pass
    if not tomasberg_found:
        # print("[DEBUG] Tomasberg NOT found in locations!")
        pass
    # print(f"[DEBUG] Root locations: {[node.get_name() for node in root_nodes]}")
    
    # Debug: Print the complete tree structure
    def print_tree_debug(node, indent=0):
        # print("  " * indent + f"- {node.get_name()} (ID: {node.get_id()}, Depth: {node.depth})")
        for child in sorted(node.children, key=lambda x: x.get_name()):
            print_tree_debug(child, indent + 1)
    # print("[DEBUG] Complete location tree structure:")
    # for root in sorted(root_nodes, key=lambda x: x.get_name()):
    #     print_tree_debug(root)
    
    # Convert tree structure back to the format expected by the rest of the code
    loc_children = defaultdict(list)
    root_locations = []
    
    def process_node(node):
        # Add this node's children to the loc_children dict
        for child in node.children:
            loc_children[node.get_id()].append(child.location)
            process_node(child)
    
    for root_node in root_nodes:
        root_locations.append(root_node.location)
        process_node(root_node)
    
    chars_by_location = defaultdict(list)
    chars_without_location = characters
    for char in characters:
        loc_id = char.get('location_id')
        if loc_id and loc_id in location_by_id:
            parent_entity_id = location_by_id[loc_id]['entity']['id']
            chars_by_location[parent_entity_id].append(char)
    def write_location(loc, depth=5):
        ent = loc['entity']
        loc_name = loc.get('name') or ent.get('name', 'Unnamed Location')
        anchor = create_anchor_label(loc_name)
        pluses = '+' * depth
        # print(f"[DEBUG] Rendering location: {loc_name}, depth: {depth}")
        lines = []
        # Add extra newlines before h7, h8, or lower headers
        extra_newlines = '\n\n' if depth >= 7 else ''
        lines.append(f'\n{extra_newlines}{"#" * depth} {md_escape(loc_name)} (({pluses}{anchor}))\n\n')
        entry_html = loc.get('entry') or ent.get('entry') or ''
        entry_cleaned = convert_mentions_in_html(entry_html)
        entry_md = replace_mentions(entry_cleaned, entity_map)
        details = []
        if is_private_obj(loc):
            details.append("- **Privát:** Igen")
        if details:
            # Ensure a blank line before the list
            details_block = '\n'.join(details)
            if not details_block.startswith('\n- '):
                details_block = '\n' + details_block
            lines.append("\n---\n**Részletek:**\n\n" + details_block + "\n\n")
        if entry_md.strip():
            lines.append(f"{entry_md}\n\n")
        chars_here = chars_by_location.get(ent['id'], [])
        if chars_here:
            lines.append(f"**Karakterek ezen a helyszínen: {md_escape(loc_name)}:**\n\n")
            for c in sorted(chars_here, key=lambda x: x.get('name') or x['entity'].get('name', '')):
                ent = c.get('entity', {})
                c_name = c.get('name') or c['entity'].get('name', 'Unnamed Character')
                c_anchor = create_anchor_label(c_name)
                lines.append(f"- [{md_escape(c_name)}](#{c_anchor})\n")
            lines.append('\n')
        for child_loc in sorted(loc_children.get(loc['id'], []), key=lambda x: x.get('name') or x['entity'].get('name', '')):
            lines.append(write_location(child_loc, depth + 1))
        return ''.join(lines)
    # --- Races and Subraces ---
    race_children = defaultdict(list)
    root_races = []
    for race in races:
        parent_id = race.get('race_id')
        if parent_id:
            race_children[parent_id].append(race)
        else:
            root_races.append(race)
    def write_race(race, depth=2):
        ent = race.get('entity', {})
        race_name = race.get('name') or ent.get('name', 'Unnamed Race')
        anchor = create_anchor_label(race_name)
        pluses = '+' * depth
        # print(f"[DEBUG] Rendering race: {race_name}, depth: {depth}")
        lines = []
        # Add extra newlines before h7, h8, or lower headers
        extra_newlines = '\n\n' if depth >= 7 else ''
        lines.append(f'\n{extra_newlines}{"#" * depth} {md_escape(race_name)} (({pluses}{anchor}))\n\n')
        entry_html = race.get('entry') or ent.get('entry') or ''
        entry_cleaned = convert_mentions_in_html(entry_html)
        entry_md = replace_mentions(entry_cleaned, entity_map)
        details = []
        if is_private_obj(race):
            details.append("- **Privát:** Igen")
        if details:
            # Ensure a blank line before the list
            details_block = '\n'.join(details)
            if not details_block.startswith('\n- '):
                details_block = '\n' + details_block
            lines.append("\n---\n**Részletek:**\n" + details_block + "\n\n")
        if entry_md.strip():
            lines.append(f"{entry_md}\n\n")
        for child_race in sorted(race_children.get(race['id'], []), key=lambda x: x.get('name') or x.get('entity', {}).get('name', '')):
            lines.append(write_race(child_race, depth + 1))
        return ''.join(lines)
    def generate_organizations(organizations, entity_map, character_id_to_entity_id):
        markdown = "\n# Szervezetek  ((+szervezetek))\n\n"
        for org in sorted(organizations, key=lambda o: o.get('name') or o.get('entity', {}).get('name', '')):
            ent = org.get('entity', {})
            org_name = org.get('name') or ent.get('name', 'Unnamed Organization')
            anchor = create_anchor_label(org_name)
            pluses = '++'
            markdown += f"## {md_escape(org_name)} (({pluses}{anchor}))\n\n"
            entry = ent.get('entry')
            details = []
            if is_private_obj(org):
                details.append("- **Privát:** Igen")
            if details:
                # Ensure a blank line before the list
                details_block = '\n'.join(details)
                if not details_block.startswith('\n- '):
                    details_block = '\n' + details_block
                markdown += "\n---\n**Részletek:**\n" + details_block + "\n\n"
            if entry:
                entry_md = replace_mentions(entry, entity_map)
                markdown += f"{entry_md}\n\n"
            members = org.get('members', [])
            if members:
                markdown += "**Members:**\n\n"
                for member in members:
                    char_id = member.get('character_id')
                    entity_id = character_id_to_entity_id.get(char_id)
                    char_info = entity_map.get(entity_id)
                    if char_info:
                        char_name = char_info['name']
                        char_anchor = create_anchor_label(char_name)
                        role = member.get('role')
                        if role:
                            markdown += f"- [{md_escape(char_name)}](#{char_anchor}) ({md_escape(role)})\n"
                        else:
                            markdown += f"- [{md_escape(char_name)}](#{char_anchor})\n"
                    else:
                        markdown += f"- **Unknown member {char_id}**\n"
                markdown += "\n"
        return markdown
    def write_section(title, entries, entity_map, section_slug):
        markdown = f"\n# {title} ((+{section_slug}))\n\n"
        for e in sorted(entries, key=lambda e: e.get('name') or e.get('entity', {}).get('name', '')):
            ent = e.get('entity', {})
            name = e.get('name') or ent.get('name', f'Unnamed {title}')
            anchor = create_anchor_label(name)
            pluses = '++'
            markdown += f"## {md_escape(name)} (({pluses}{anchor}))\n\n"
            entry_html = e.get('entry') or e.get('entity', {}).get('entry') or ''
            entry_cleaned = convert_mentions_in_html(entry_html)
            entry_md = replace_mentions(entry_cleaned, entity_map)
            details = []
            if is_private_obj(e):
                details.append("- **Privát:** Igen")
            # Add location as a markdown link if available
            loc_name = None
            if e.get('location_id') and e.get('location_id') in location_by_id:
                loc = location_by_id[e['location_id']]
                loc_name = loc.get('name') or loc.get('entity', {}).get('name')
            if loc_name:
                loc_anchor = create_anchor_label(loc_name)
                details.append(f"- **Tartózkodási hely:** [{md_escape(loc_name)}](#{loc_anchor})")
            if 'type' in ent and ent['type']:
                details.append(f"- **Típus:** {md_escape(ent['type'])}")
            if ent.get('tags'):
                tag_names = [tag.get('name', '') for tag in ent.get('tags', [])]
                details.append(f"- **Címkék:** {', '.join(tag_names)}")
            if 'age' in e and e['age']:
                details.append(f"- **Életkor:** {e['age']}")
            if 'gender' in e and  e['gender']:
                details.append(f"- **Nem:** {e['gender']}")
            details_md = ""
            if details:
                # Ensure a blank line before the list
                details_block = '\n'.join(details)
                if not details_block.startswith('\n- '):
                    details_block = '\n' + details_block
                details_md = "\n\n---\n**Részletek:**\n" + details_block + "\n\n"
            full_entry = details_md + entry_md
            markdown += f"{full_entry}\n"
            pivot_members = e.get('pivotMembers', [])
            if pivot_members:
                markdown += "**Családtagok:**\n\n"
                for member in pivot_members:
                    char_id = member.get('character_id')
                    entity_id = character_id_to_entity_id.get(char_id)
                    char_info = entity_map.get(entity_id)
                    if char_info:
                        char_name = char_info['name']
                        char_anchor = create_anchor_label(char_name)
                        markdown += f"- [{md_escape(char_name)}](#{char_anchor})\n"
                    else:
                        markdown += f"- **Unknown member {char_id}**\n"
                markdown += "\n"
            markdown += "\n---\n"
        return markdown

    output_lines = []
    output_lines.append('# Könyv ((+konyv))')
    output_lines.append('')
    loc_section = []
    # Debug: Check what root locations we have
    # print(f"[DEBUG] Root locations for rendering: {[loc.get('name') for loc in root_locations]}")
    
    # Render all locations, starting from root locations
    for root_loc in sorted(root_locations, key=lambda x: x.get('name') or x['entity'].get('name', '')):
        loc_section.extend(write_location(root_loc).split('\n'))
    if loc_section:
        add_section(loc_section, output_lines)
    chars_section = []
    if chars_without_location:
        chars_section.append('# Helyszín nélküli karakterek  ((+chars_withour_loc))')
        chars_section.append('')
        for c in sorted(chars_without_location, key=lambda x: x.get('name') or x.get('entity', {} ).get('name', '')):
            c_ent = c['entity']
            c_name = c.get('name') or c_ent.get('name', 'Unnamed Character')
            anchor = create_anchor_label(c_name)
            entry_html = c.get('entry') or ""
            entry_cleaned = convert_mentions_in_html(entry_html)
            entry = replace_mentions(entry_cleaned, entity_map)
            details = []
            if is_private_obj(c):
                details.append("- **Privát:** Igen")
            race_name = None
            race_id = None
            if 'character_races' in c and c['character_races']:
                race = c['character_races'][0].get('race')
                if race:
                    race_name = race.get('name')
                    race_id = race.get('id')
            elif 'characterRaces' in c and c['characterRaces']:
                race = c['characterRaces'][0].get('race')
                if race:
                    race_name = race.get('name')
                    race_id = race.get('id')
            if race_name:
                if race_id:
                    race_anchor = create_anchor_label(race_name)
                    details.append(f"- **Faj:** [{md_escape(race_name)}](#{race_anchor})")
                else:
                    details.append(f"- **Faj:** {md_escape(race_name)}")
            loc_name = None
            if c.get('location_id') and c.get('location_id') in location_by_id:
                loc = location_by_id[c['location_id']]
                loc_name = loc.get('name') or loc.get('entity', {}).get('name')
            if loc_name:
                loc_anchor = create_anchor_label(loc_name)
                details.append(f"- **Tartózkodási hely:** [{md_escape(loc_name)}](#{loc_anchor})")
            family_name = None
            family_id = None
            if 'character_families' in c and c['character_families']:
                fam = c['character_families'][0].get('family')
                if fam:
                    family_name = fam.get('name')
                    family_id = fam.get('id')
            elif 'characterFamilies' in c and c['characterFamilies']:
                fam_id = c['characterFamilies'][0].get('family_id')
                fam = next((f for f in families if f['id'] == fam_id), None)
                if fam:
                    family_name = fam.get('name')
                    family_id = fam.get('id')
            if family_name:
                if family_id:
                    family_anchor = create_anchor_label(family_name)
                    details.append(f"- **Család:** [{md_escape(family_name)}](#{family_anchor})")
                else:
                    details.append(f"- **Család:** {md_escape(family_name)}")
            char_type = c.get('type') or c_ent.get('type')
            if char_type:
                details.append(f"- **Típus:** {md_escape(char_type)}")
            if c.get('age'):
                details.append(f"- **Életkor:** {md_escape(str(c['age']))}")
            if c.get('sex'):
                details.append(f"- **Nem:** {md_escape(str(c['sex']))}")
            elif c.get('gender'):
                details.append(f"- **Nem:** {md_escape(str(c['gender']))}")
            is_dead = c.get('is_dead') or c_ent.get('is_dead')
            if is_dead:
                details.append(f"- **Halott:** Igen")
            details_md = ""
            if details:
                # Ensure a blank line before the list
                details_block = '\n'.join(details)
                if not details_block.startswith('\n- '):
                    details_block = '\n' + details_block
                details_md = "\n\n---\n**Részletek:**\n" + details_block + "\n\n"
            chars_section.append(f"## {md_escape(c_name)} ((++{anchor}))\n\n")
            chars_section.append(f"{details_md}{entry}\n\n---\n")
    if chars_section:
        add_section(chars_section, output_lines)
    events_section = []
    if events:
        events_section.append('# Események ((+Esemenyek))')
        events_section.append('')
        for event in sorted(events, key=lambda e: e.get('name') or e.get('entity', {}).get('name', '')):
            ent = event.get('entity', {})
            if ent.get('is_private'):
                continue
            event_ent = event['entity']
            event_id = event_ent['id']
            event_name = event.get('name') or event_ent.get('name', 'Unnamed Event')
            entry = replace_mentions(event.get('entry') or "", entity_map)
            events_section.append(f'\n<a name="entity-{event_id}"></a>')
            events_section.append(f"## {md_escape(event_name)}\n")
            events_section.append(f"{entry}\n\n---\n")
    if events_section:
        add_section(events_section, output_lines)
    orgs_section = generate_organizations(organizations, entity_map, character_id_to_entity_id).split('\n')
    if orgs_section:
        add_section(orgs_section, output_lines)
    notes_section = write_section("Jegyzetek", notes, entity_map, "jegyzetek").split('\n')
    if notes_section:
        add_section(notes_section, output_lines)
    items_section = write_section("Tárgyak", items, entity_map, "targyak").split('\n')
    if items_section:
        add_section(items_section, output_lines)
    families_section = write_section("Családok", families, entity_map, "csaladok").split('\n')
    if families_section:
        add_section(families_section, output_lines)
    races_section = []
    races_section.append('# Fajok ((+fajok))')
    races_section.append('')
    for root_race in sorted(root_races, key=lambda x: x.get('name') or x.get('entity', {}).get('name', '')):
        races_section.extend(write_race(root_race).split('\n'))
    if races_section:
        add_section(races_section, output_lines)
    output_lines.append('---')
    output_lines.append("## Generálási beállítások\n")
    output_lines.append(f"- **Privát entitások megjelenítése:** {'Igen' if include_private else 'Nem'}\n")
    if not output_lines:
        # print('[DEBUG] generate_worldbook: output_lines is empty, returning empty string')
        return ''
    result = '\n'.join(output_lines)
    # print(f'[DEBUG] generate_worldbook: returning {len(result)} characters')
    return result 