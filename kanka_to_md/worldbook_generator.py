from typing import List, Dict, Any
from collections import defaultdict
from .markdown_utils import create_anchor_label, convert_mentions_in_html, replace_mentions, md_escape
from .localization import get_chapter_title, get_chapter_slug, get_ui_text, validate_language
import re
import os

def get_entity_image_path(entity_data, gallery_dir):
    """
    Get the image path for an entity if it has an associated image.
    Args:
        entity_data: Entity data dictionary
        gallery_dir: Directory containing downloaded images
    Returns:
        str: Relative path to image file, or None if no image
    """
    # Check if entity has an image UUID (try both root and entity field)
    image_uuid = entity_data.get('image_uuid')
    if not image_uuid:
        # Try to get from entity field
        entity = entity_data.get('entity', {})
        image_uuid = entity.get('image_uuid')
    
    # For campaigns, also check the 'image' field
    if not image_uuid and entity_data.get('id') and not entity_data.get('entity'):
        # This might be a campaign entity
        image_path = entity_data.get('image')
        if image_path:
            # Extract filename from path
            filename = os.path.basename(image_path)
            # Look for the image file in the gallery directory
            for gallery_file in os.listdir(gallery_dir):
                if gallery_file == filename:
                    # Skip JSON metadata files, only return actual image files
                    if not gallery_file.endswith('.json'):
                        # Return relative path from kanka_jsons directory
                        return f"gallery/{gallery_file}"
            
            # If not found with exact match, try partial match (for cases where extension might differ)
            filename_without_ext = os.path.splitext(filename)[0]
            for gallery_file in os.listdir(gallery_dir):
                if gallery_file.startswith(filename_without_ext) and not gallery_file.endswith('.json'):
                    # Return relative path from kanka_jsons directory
                    return f"gallery/{gallery_file}"
    
    if not image_uuid:
        return None
    
    # Look for the image file in the gallery directory
    for filename in os.listdir(gallery_dir):
        if filename.startswith(image_uuid) and '.' in filename:
            # Skip JSON metadata files, only return actual image files
            if not filename.endswith('.json'):
                # Return relative path from kanka_jsons directory
                return f"gallery/{filename}"
    
    return None

def get_entity_image_markdown(entity_data, gallery_dir, entity_name):
    """
    Generate markdown image syntax for an entity if it has an image.
    Args:
        entity_data: Entity data dictionary
        gallery_dir: Directory containing downloaded images
        entity_name: Name of the entity for alt text
    Returns:
        str: Markdown image syntax or empty string if no image
    """
    image_path = get_entity_image_path(entity_data, gallery_dir)
    if not image_path:
        return ""
    
    # Generate markdown image syntax
    return f"\n![{entity_name}]({image_path})\n"

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

def generate_worldbook(entities: dict, include_private=False, include_posts=True, language: str = 'en') -> str:
    # Validate and set language
    language = validate_language(language)
    
    # Unpack known types for legacy rendering order
    campaign = entities.get('campaign', {})
    locations = entities.get('locations', {})
    characters = entities.get('characters', [])
    charlocations = entities.get('charlocations', {})
    organizations = entities.get('organizations', [])
    events = entities.get('events', [])
    entity_map = entities.get('entity_map', {})
    character_id_to_entity_id = entities.get('character_id_to_entity_id', {})
    notes = entities.get('notes', [])
    items = entities.get('items', [])
    families = entities.get('families', [])
    races = entities.get('races', [])
    journals = entities.get('journals', [])
    calendars = entities.get('calendars', [])
    tags = entities.get('tags', [])
    quests = entities.get('quests', [])
    maps = entities.get('maps', [])
    timelines = entities.get('timelines', [])

    # Generic tree node class for all hierarchical entities
    class TreeNode:
        def __init__(self, entity_data):
            self.entity = entity_data
            self.children = []
            self.depth = 0
            # Handle different parent field names for different entity types
            self.parent_id = None
            entity_type = entity_data.get('entity', {}).get('type', '')
            if entity_type is None:
                entity_type = ''
            entity_type = entity_type.lower()
            
            if entity_type == 'journal':
                # Journals use journal_id for parent relationship
                self.parent_id = entity_data.get('journal_id')
            elif entity_type == 'location':
                # Locations use location_id for parent relationship
                self.parent_id = entity_data.get('location_id')
            elif entity_type == 'race':
                # Races use race_id for parent relationship
                self.parent_id = entity_data.get('race_id')
            elif entity_type == 'quest':
                # Quests use quest_id for parent relationship
                self.parent_id = entity_data.get('quest_id')
            elif entity_type == 'note':
                # Notes use note_id for parent relationship
                self.parent_id = entity_data.get('note_id')
            elif entity_type == 'family':
                # Families use family_id for parent relationship
                self.parent_id = entity_data.get('family_id')
            elif entity_type == 'organisation':
                # Organizations use organisation_id for parent relationship
                self.parent_id = entity_data.get('organisation_id')
            elif entity_type == 'item':
                # Items use item_id for parent relationship
                self.parent_id = entity_data.get('item_id')
            elif entity_type == 'calendar':
                # Calendars use calendar_id for parent relationship
                self.parent_id = entity_data.get('calendar_id')
            elif entity_type == 'timeline':
                # Timelines use timeline_id for parent relationship
                self.parent_id = entity_data.get('timeline_id')
            elif entity_type == 'map':
                # Maps use map_id for parent relationship
                self.parent_id = entity_data.get('map_id')
            elif entity_type == 'tag':
                # Tags use tag_id for parent relationship
                self.parent_id = entity_data.get('tag_id')
            else:
                # Default to parent_id for other types
                self.parent_id = entity_data.get('parent_id') or entity_data.get('entity', {}).get('parent_id')
            
            self.entity_id = entity_data.get('id') or entity_data.get('entity', {}).get('id')
        
        def add_child(self, child_node):
            self.children.append(child_node)
            child_node.depth = self.depth + 1
        
        def get_name(self):
            return self.entity.get('name') or self.entity.get('entity', {}).get('name', 'Unnamed')
        
        def get_id(self):
            return self.entity_id
    
    # Build hierarchical tree for any entity type
    def build_entity_tree(entities_list):
        if not entities_list:
            return []
        
        # Create nodes
        nodes = {}
        root_nodes = []
        
        for entity in entities_list:
            node = TreeNode(entity)
            nodes[node.get_id()] = node
        
        # Build parent-child relationships
        for node in nodes.values():
            if node.parent_id and node.parent_id in nodes:
                parent = nodes[node.parent_id]
                parent.add_child(node)
            else:
                root_nodes.append(node)
        
        return root_nodes
    
    # Write hierarchical entity with proper indentation
    def write_hierarchical_entity(entity, depth=0, max_depth=5):
        if depth > max_depth:
            return []
        
        lines = []
        ent = entity.get('entity', {})
        name = entity.get('name') or ent.get('name', 'Unnamed')
        anchor = create_anchor_label(name)
        pluses = '+' * (depth + 2)
        
        # Use proper markdown header without indentation spaces
        # The indentation will be handled by CSS in the HTML output
        lines.append(f"## {md_escape(name)} (({pluses}{anchor}))")
        lines.append("")
        
        # Add entity image if available
        gallery_dir = os.path.join(os.path.dirname(__file__), 'kanka_jsons', 'gallery')
        if os.path.exists(gallery_dir):
            image_markdown = get_entity_image_markdown(entity, gallery_dir, name)
            if image_markdown:
                lines.append(image_markdown)
        
        entry_html = entity.get('entry') or ent.get('entry') or ''
        entry_cleaned = convert_mentions_in_html(entry_html)
        entry_md = replace_mentions(entry_cleaned, entity_map)
        
        details = []
        if is_private_obj(entity):
            details.append(f"- **{get_ui_text('private', language)}:** {get_ui_text('yes', language)}")
        
        # Add location as a markdown link if available
        loc_name = None
        if entity.get('location_id') and entity.get('location_id') in location_by_id:
            loc = location_by_id[entity['location_id']]
            loc_name = loc.get('name') or loc.get('entity', {}).get('name')
        if loc_name:
            loc_anchor = create_anchor_label(loc_name)
            details.append(f"- **{get_ui_text('location', language)}:** [{md_escape(loc_name)}](#{loc_anchor})")
        
        if 'type' in ent and ent['type']:
            details.append(f"- **{get_ui_text('type', language)}:** {md_escape(ent['type'])}")
        
        if ent.get('tags'):
            tag_names = []
            for tag in ent.get('tags', []):
                if isinstance(tag, dict) and 'name' in tag:
                    tag_names.append(tag.get('name', ''))
                elif isinstance(tag, str):
                    tag_names.append(tag)
                # Skip if tag is an integer or other non-string/non-dict type
            if tag_names:
                details.append(f"- **{get_ui_text('tags', language)}:** {', '.join(tag_names)}")
        
        if 'age' in entity and entity['age']:
            details.append(f"- **{get_ui_text('age', language)}:** {entity['age']}")
        
        if 'gender' in entity and entity['gender']:
            details.append(f"- **{get_ui_text('gender', language)}:** {entity['gender']}")
        
        details_md = ""
        if details:
            details_block = '\n'.join(details)
            if not details_block.startswith('\n- '):
                details_block = '\n' + details_block
            details_md = f"\n\n---\n**{get_ui_text('details', language)}:**\n" + details_block + "\n\n"
        
        full_entry = details_md + entry_md
        lines.append(f"{full_entry}")
        
        # Add family members if this is a family
        pivot_members = entity.get('pivotMembers', [])
        if pivot_members:
            lines.append(f"**{get_ui_text('family_members', language)}:**\n")
            for member in pivot_members:
                char_id = member.get('character_id')
                entity_id = character_id_to_entity_id.get(char_id)
                char_info = entity_map.get(entity_id)
                if char_info:
                    char_name = char_info['name']
                    char_anchor = create_anchor_label(char_name)
                    lines.append(f"- [{md_escape(char_name)}](#{char_anchor})")
                else:
                    lines.append(f"- **Unknown member {char_id}**")
            lines.append("")
        
        # Add posts as subentities if they exist and include_posts is True
        posts = ent.get('posts', [])
        if posts and include_posts:
            # Sort posts by position if available, otherwise by creation date
            sorted_posts = sorted(posts, key=lambda p: (p.get('position', 0), p.get('created_at', '')))
            
            for post in sorted_posts:
                # Skip private posts if include_private is False
                # visibility_id: 1 = Public, 2 = Private (Admin only), 3 = Private (Self only)
                if not include_private and post.get('visibility_id', 1) != 1:
                    continue
                
                post_name = post.get('name', get_ui_text('unnamed_post', language))
                post_entry = post.get('entry', '')
                
                # Skip posts with empty or minimal content (like just <br>)
                if not post_entry or post_entry.strip() in ['<br>', '<br/>', '<br />', '']:
                    continue
                
                # Create anchor for the post
                post_anchor = create_anchor_label(f"{name}_{post_name}")
                post_pluses = '+' * (depth + 3)  # One level deeper than the parent entity
                
                # Add post as subentity with header level depth + 3 (h3 for depth 0, h4 for depth 1, etc.)
                lines.append(f"### {md_escape(post_name)} (({post_pluses}{post_anchor}))")
                lines.append("")
                
                # Process post content
                post_entry_cleaned = convert_mentions_in_html(post_entry)
                post_entry_md = replace_mentions(post_entry_cleaned, entity_map)
                
                lines.append(f"{post_entry_md}\n")
                lines.append("---")
                lines.append("")
        
        lines.append("---")
        return lines
    
    # Write hierarchical section with tree traversal
    def write_hierarchical_section(title, entities_list, entity_map, section_slug, max_depth=5):
        if not entities_list:
            return []
        
        lines = []
        lines.append(f"# {title} ((+{section_slug}))")
        lines.append("")
        
        # Build tree
        root_nodes = build_entity_tree(entities_list)
        
        # Traverse tree and write entities
        def traverse_and_write(node, depth=0):
            if depth > max_depth:
                return
            
            # Write this node
            entity_lines = write_hierarchical_entity(node.entity, depth, max_depth)
            lines.extend(entity_lines)
            
            # Sort children by name and recursively write them
            sorted_children = sorted(node.children, key=lambda n: n.get_name())
            for child in sorted_children:
                traverse_and_write(child, depth + 1)
        
        # Sort root nodes by name and traverse
        sorted_roots = sorted(root_nodes, key=lambda n: n.get_name())
        for root in sorted_roots:
            traverse_and_write(root)
        
        return lines

    # Simple function that adds all lines without pagination
    def add_section(section_lines, output_lines):
        output_lines.extend(section_lines)

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

    if journals is None:
        journals = []

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
    

    def write_location(loc, depth=0, max_depth=10):
        if depth > max_depth:
            return []
        
        ent = loc['entity']
        loc_name = loc.get('name') or ent.get('name', 'Unnamed Location')
        anchor = create_anchor_label(loc_name)
        
        # Calculate proper header level: h2 for root locations, h3 for children, etc.
        header_level = depth + 2
        header_markers = '#' * header_level
        
        # Calculate pluses for anchor (depth + 2 to match other entities)
        pluses = '+' * (depth + 2)
        
        lines = []
        
        # Add extra newlines before deeper headers for better readability
        extra_newlines = '\n\n' if depth >= 4 else ''
        lines.append(f'\n{extra_newlines}{header_markers} {md_escape(loc_name)} (({pluses}{anchor}))\n\n')
        
        # Add location image if available
        gallery_dir = os.path.join(os.path.dirname(__file__), 'kanka_jsons', 'gallery')
        if os.path.exists(gallery_dir):
            image_markdown = get_entity_image_markdown(loc, gallery_dir, loc_name)
            if image_markdown:
                lines.append(image_markdown)
        
        entry_html = loc.get('entry') or ent.get('entry') or ''
        entry_cleaned = convert_mentions_in_html(entry_html)
        entry_md = replace_mentions(entry_cleaned, entity_map)
        details = []
        if is_private_obj(loc):
            details.append(f"- **{get_ui_text('private', language)}:** {get_ui_text('yes', language)}")
        if details:
            # Ensure a blank line before the list
            details_block = '\n'.join(details)
            if not details_block.startswith('\n- '):
                details_block = '\n' + details_block
            lines.append(f"\n---\n**{get_ui_text('details', language)}:**\n\n" + details_block + "\n\n")
        if entry_md.strip():
            lines.append(f"{entry_md}\n\n")
        chars_here = chars_by_location.get(ent['id'], [])
        if chars_here:
            lines.append(f"**{get_ui_text('characters_at_location', language)}: {md_escape(loc_name)}:**\n\n")
            for c in sorted(chars_here, key=lambda x: x.get('name') or x['entity'].get('name', '')):
                ent = c.get('entity', {})
                c_name = c.get('name') or c['entity'].get('name', 'Unnamed Character')
                c_anchor = create_anchor_label(c_name)
                lines.append(f"- [{md_escape(c_name)}](#{c_anchor})\n")
            lines.append('\n')
        
        # Recursively write child locations with proper depth management
        for child_loc in sorted(loc_children.get(loc['id'], []), key=lambda x: x.get('name') or x['entity'].get('name', '')):
            child_lines = write_location(child_loc, depth + 1, max_depth)
            lines.extend(child_lines)
        
        return lines
    # --- Races and Subraces ---
    race_children = defaultdict(list)
    root_races = []
    for race in races:
        parent_id = race.get('race_id')
        if parent_id:
            race_children[parent_id].append(race)
        else:
            root_races.append(race)
    def write_race(race, depth=0, max_depth=10):
        if depth > max_depth:
            return []
        
        ent = race.get('entity', {})
        race_name = race.get('name') or ent.get('name', 'Unnamed Race')
        anchor = create_anchor_label(race_name)
        
        # Calculate proper header level: h2 for root races, h3 for children, etc.
        header_level = depth + 2
        header_markers = '#' * header_level
        
        # Calculate pluses for anchor (depth + 2 to match other entities)
        pluses = '+' * (depth + 2)
        
        lines = []
        
        # Add extra newlines before deeper headers for better readability
        extra_newlines = '\n\n' if depth >= 4 else ''
        lines.append(f'\n{extra_newlines}{header_markers} {md_escape(race_name)} (({pluses}{anchor}))\n\n')
        
        # Add race image if available
        gallery_dir = os.path.join(os.path.dirname(__file__), 'kanka_jsons', 'gallery')
        if os.path.exists(gallery_dir):
            image_markdown = get_entity_image_markdown(race, gallery_dir, race_name)
            if image_markdown:
                lines.append(image_markdown)
        
        entry_html = race.get('entry') or ent.get('entry') or ''
        entry_cleaned = convert_mentions_in_html(entry_html)
        entry_md = replace_mentions(entry_cleaned, entity_map)
        details = []
        if is_private_obj(race):
            details.append(f"- **{get_ui_text('private', language)}:** {get_ui_text('yes', language)}")
        if details:
            # Ensure a blank line before the list
            details_block = '\n'.join(details)
            if not details_block.startswith('\n- '):
                details_block = '\n' + details_block
            lines.append(f"\n---\n**{get_ui_text('details', language)}:**\n" + details_block + "\n\n")
        if entry_md.strip():
            lines.append(f"{entry_md}\n\n")
        
        # Recursively write child races with proper depth management
        for child_race in sorted(race_children.get(race['id'], []), key=lambda x: x.get('name') or x.get('entity', {}).get('name', '')):
            child_lines = write_race(child_race, depth + 1, max_depth)
            lines.extend(child_lines)
        
        return lines
    def generate_organizations(organizations, entity_map, character_id_to_entity_id, language='en'):
        markdown = f"\n# {get_chapter_title('organizations', language)}  ((+{get_chapter_slug('organizations', language)}))\n\n"
        for org in sorted(organizations, key=lambda o: o.get('name') or o.get('entity', {}).get('name', '')):
            ent = org.get('entity', {})
            org_name = org.get('name') or ent.get('name', 'Unnamed Organization')
            anchor = create_anchor_label(org_name)
            pluses = '++'
            markdown += f"## {md_escape(org_name)} (({pluses}{anchor}))\n\n"
            
            # Add organization image if available
            gallery_dir = os.path.join(os.path.dirname(__file__), 'kanka_jsons', 'gallery')
            if os.path.exists(gallery_dir):
                image_markdown = get_entity_image_markdown(org, gallery_dir, org_name)
                if image_markdown:
                    markdown += image_markdown
            
            entry = ent.get('entry')
            details = []
            if is_private_obj(org):
                details.append(f"- **{get_ui_text('private', language)}:** {get_ui_text('yes', language)}")
            if details:
                # Ensure a blank line before the list
                details_block = '\n'.join(details)
                if not details_block.startswith('\n- '):
                    details_block = '\n' + details_block
                markdown += f"\n---\n**{get_ui_text('details', language)}:**\n" + details_block + "\n\n"
            if entry:
                entry_md = replace_mentions(entry, entity_map)
                markdown += f"{entry_md}\n\n"
            members = org.get('members', [])
            if members:
                markdown += f"**{get_ui_text('members', language)}:**\n\n"
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
                        markdown += f"- **{get_ui_text('unknown_member', language)} {char_id}**\n"
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
            
            # Add entity image if available
            gallery_dir = os.path.join(os.path.dirname(__file__), 'kanka_jsons', 'gallery')
            if os.path.exists(gallery_dir):
                image_markdown = get_entity_image_markdown(e, gallery_dir, name)
                if image_markdown:
                    markdown += image_markdown
            
            entry_html = e.get('entry') or e.get('entity', {}).get('entry') or ''
            entry_cleaned = convert_mentions_in_html(entry_html)
            entry_md = replace_mentions(entry_cleaned, entity_map)
            details = []
            if is_private_obj(e):
                details.append(f"- **{get_ui_text('private', language)}:** {get_ui_text('yes', language)}")
            # Add location as a markdown link if available
            loc_name = None
            if e.get('location_id') and e.get('location_id') in location_by_id:
                loc = location_by_id[e['location_id']]
                loc_name = loc.get('name') or loc.get('entity', {}).get('name')
            if loc_name:
                loc_anchor = create_anchor_label(loc_name)
                details.append(f"- **{get_ui_text('location', language)}:** [{md_escape(loc_name)}](#{loc_anchor})")
            if 'type' in ent and ent['type']:
                details.append(f"- **{get_ui_text('type', language)}:** {md_escape(ent['type'])}")
            if ent.get('tags'):
                tag_names = [tag.get('name', '') for tag in ent.get('tags', [])]
                details.append(f"- **{get_ui_text('tags', language)}:** {', '.join(tag_names)}")
            if 'age' in e and e['age']:
                details.append(f"- **{get_ui_text('age', language)}:** {e['age']}")
            if 'gender' in e and  e['gender']:
                details.append(f"- **{get_ui_text('gender', language)}:** {e['gender']}")
            details_md = ""
            if details:
                # Ensure a blank line before the list
                details_block = '\n'.join(details)
                if not details_block.startswith('\n- '):
                    details_block = '\n' + details_block
                details_md = f"\n\n---\n**{get_ui_text('details', language)}:**\n" + details_block + "\n\n"
            full_entry = details_md + entry_md
            markdown += f"{full_entry}\n"
            pivot_members = e.get('pivotMembers', [])
            if pivot_members:
                markdown += f"**{get_ui_text('family_members', language)}:**\n\n"
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

    # Render sections in order with hierarchy support
    output_lines = []
    
    # Campaign Overview (first chapter)
    if campaign:
        campaign_section = []
        campaign_name = campaign.get('name', 'Campaign Overview')
        campaign_section.append(f"# {md_escape(campaign_name)} ((+campaign-overview))")
        campaign_section.append('')
        
        # Add campaign image if available
        gallery_dir = os.path.join(os.path.dirname(__file__), 'kanka_jsons', 'gallery')
        if os.path.exists(gallery_dir):
            image_markdown = get_entity_image_markdown(campaign, gallery_dir, campaign_name)
            if image_markdown:
                campaign_section.append(image_markdown)
        
        # Process campaign entry/description
        entry_html = campaign.get('entry', '')
        if entry_html:
            entry_cleaned = convert_mentions_in_html(entry_html)
            entry_md = replace_mentions(entry_cleaned, entity_map)
            campaign_section.append(f"{entry_md}\n")
        
        # Add campaign details (only excerpt, no timestamps)
        details = []
        if campaign.get('excerpt'):
            details.append(f"- **{get_ui_text('excerpt', language)}:** {md_escape(campaign['excerpt'])}")
        
        if details:
            details_block = '\n'.join(details)
            campaign_section.append(f"\n---\n**{get_ui_text('details', language)}:**\n")
            campaign_section.append(details_block)
            campaign_section.append("\n")
        
        campaign_section.append("---")
        add_section(campaign_section, output_lines)
    
    # Locations (keep existing hierarchical logic)
    loc_section = []
    loc_section.append(f"# {get_chapter_title('locations', language)} ((+{get_chapter_slug('locations', language)}))")
    loc_section.append('')
    for root_loc in sorted(root_locations, key=lambda x: x.get('name') or x['entity'].get('name', '')):
        loc_section.extend(write_location(root_loc))
    if loc_section:
        add_section(loc_section, output_lines)
    
    # Characters without location (keep existing logic)
    chars_section = []
    if chars_without_location:
        chars_section.append(f"# {get_chapter_title('characters', language)}  ((+{get_chapter_slug('characters', language)}))")
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
                details.append(f"- **{get_ui_text('private', language)}:** {get_ui_text('yes', language)}")
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
                    details.append(f"- **{get_ui_text('race', language)}:** [{md_escape(race_name)}](#{race_anchor})")
                else:
                    details.append(f"- **{get_ui_text('race', language)}:** {md_escape(race_name)}")
            loc_name = None
            if c.get('location_id') and c.get('location_id') in location_by_id:
                loc = location_by_id[c['location_id']]
                loc_name = loc.get('name') or loc.get('entity', {}).get('name')
            if loc_name:
                loc_anchor = create_anchor_label(loc_name)
                details.append(f"- **{get_ui_text('location', language)}:** [{md_escape(loc_name)}](#{loc_anchor})")
            family_name = None
            family_id = None
            if 'character_families' in c and c['character_families']:
                family = c['character_families'][0].get('family')
                if family:
                    family_name = family.get('name')
                    family_id = family.get('id')
            elif 'characterFamilies' in c and c['characterFamilies']:
                family = c['characterFamilies'][0].get('family')
                if family:
                    family_name = family.get('name')
                    family_id = family.get('id')
            if family_name:
                if family_id:
                    family_anchor = create_anchor_label(family_name)
                    details.append(f"- **{get_ui_text('family', language)}:** [{md_escape(family_name)}](#{family_anchor})")
                else:
                    details.append(f"- **{get_ui_text('family', language)}:** {md_escape(family_name)}")
            if c.get('age'):
                details.append(f"- **{get_ui_text('age', language)}:** {md_escape(str(c['age']))}")
            if c.get('sex'):
                details.append(f"- **{get_ui_text('gender', language)}:** {md_escape(str(c['sex']))}")
            elif c.get('gender'):
                details.append(f"- **{get_ui_text('gender', language)}:** {md_escape(str(c['gender']))}")
            is_dead = c.get('is_dead') or c_ent.get('is_dead')
            if is_dead:
                details.append(f"- **{get_ui_text('dead', language)}:** {get_ui_text('yes', language)}")
            details_md = ""
            if details:
                # Ensure a blank line before the list
                details_block = '\n'.join(details)
                if not details_block.startswith('\n- '):
                    details_block = '\n' + details_block
                details_md = f"\n\n---\n**{get_ui_text('details', language)}:**\n" + details_block + "\n\n"
            chars_section.append(f"## {md_escape(c_name)} ((++{anchor}))\n\n")
            
            # Add character image if available
            gallery_dir = os.path.join(os.path.dirname(__file__), 'kanka_jsons', 'gallery')
            if os.path.exists(gallery_dir):
                image_markdown = get_entity_image_markdown(c, gallery_dir, c_name)
                if image_markdown:
                    chars_section.append(image_markdown)
            
            chars_section.append(f"{details_md}{entry}\n")
            
            # Add posts as subentities if they exist for characters and include_posts is True
            c_ent = c.get('entity', {})
            posts = c_ent.get('posts', [])
            if posts and include_posts:
                # Sort posts by position if available, otherwise by creation date
                sorted_posts = sorted(posts, key=lambda p: (p.get('position', 0), p.get('created_at', '')))
                
                for post in sorted_posts:
                    # Skip private posts if include_private is False
                    # visibility_id: 1 = Public, 2 = Private (Admin only), 3 = Private (Self only)
                    if not include_private and post.get('visibility_id', 1) != 1:
                        continue
                    
                    post_name = post.get('name', get_ui_text('unnamed_post', language))
                    post_entry = post.get('entry', '')
                    
                    # Skip posts with empty or minimal content (like just <br>)
                    if not post_entry or post_entry.strip() in ['<br>', '<br/>', '<br />', '']:
                        continue
                    
                    # Create anchor for the post
                    post_anchor = create_anchor_label(f"{c_name}_{post_name}")
                    post_pluses = '+++'  # One level deeper than the character (++ -> +++)
                    
                    # Add post as subentity with header level h3 (one level deeper than character's h2)
                    chars_section.append(f"### {md_escape(post_name)} (({post_pluses}{post_anchor}))\n\n")
                    
                    # Process post content
                    post_entry_cleaned = convert_mentions_in_html(post_entry)
                    post_entry_md = replace_mentions(post_entry_cleaned, entity_map)
                    

                    
                    chars_section.append(f"{post_entry_md}\n")
                    chars_section.append("---")
                    chars_section.append("")
            
            chars_section.append("---\n")
    if chars_section:
        # For characters section, we want all characters to be included
        # The add_section function does pagination which might filter out some characters
        # So we'll add the characters section directly to ensure all characters are included
        output_lines.extend(chars_section)
    
    # Events (use hierarchical rendering)
    if events:
        events_section = write_hierarchical_section(get_chapter_title('events', language), events, entity_map, get_chapter_slug('events', language))
        if events_section:
            add_section(events_section, output_lines)
    
    # Organizations (keep existing logic for now)
    orgs_section = generate_organizations(organizations, entity_map, character_id_to_entity_id, language).split('\n')
    if orgs_section:
        add_section(orgs_section, output_lines)
    
    # Notes (use hierarchical rendering)
    if notes:
        notes_section = write_hierarchical_section(get_chapter_title('notes', language), notes, entity_map, get_chapter_slug('notes', language))
        if notes_section:
            add_section(notes_section, output_lines)
    
    # Items (use hierarchical rendering)
    if items:
        items_section = write_hierarchical_section(get_chapter_title('items', language), items, entity_map, get_chapter_slug('items', language))
        if items_section:
            add_section(items_section, output_lines)
    
    # Families (use hierarchical rendering)
    if families:
        families_section = write_hierarchical_section(get_chapter_title('families', language), families, entity_map, get_chapter_slug('families', language))
        if families_section:
            add_section(families_section, output_lines)
    
    # Races (keep existing hierarchical logic)
    races_section = []
    races_section.append(f"# {get_chapter_title('races', language)} ((+{get_chapter_slug('races', language)}))")
    races_section.append('')
    for root_race in sorted(root_races, key=lambda x: x.get('name') or x.get('entity', {}).get('name', '')):
        races_section.extend(write_race(root_race))
    if races_section:
        add_section(races_section, output_lines)
    
    # Journals (use hierarchical rendering)
    if journals:
        journals_section = write_hierarchical_section(get_chapter_title('journals', language), journals, entity_map, get_chapter_slug('journals', language))
        if journals_section:
            add_section(journals_section, output_lines)
    
    # Quests (use hierarchical rendering)
    if quests:
        quests_section = write_hierarchical_section(get_chapter_title('quests', language), quests, entity_map, get_chapter_slug('quests', language))
        if quests_section:
            add_section(quests_section, output_lines)
    
    # Tags (use hierarchical rendering)
    if tags:
        tags_section = write_hierarchical_section(get_chapter_title('tags', language), tags, entity_map, get_chapter_slug('tags', language))
        if tags_section:
            add_section(tags_section, output_lines)
    
    # Maps (use hierarchical rendering)
    if maps:
        maps_section = write_hierarchical_section(get_chapter_title('maps', language), maps, entity_map, get_chapter_slug('maps', language))
        if maps_section:
            add_section(maps_section, output_lines)
    
    # Calendars (use hierarchical rendering)
    if calendars:
        calendars_section = write_hierarchical_section(get_chapter_title('calendars', language), calendars, entity_map, get_chapter_slug('calendars', language))
        if calendars_section:
            add_section(calendars_section, output_lines)
    
    # Timelines (use hierarchical rendering)
    if timelines:
        timelines_section = write_hierarchical_section(get_chapter_title('timelines', language), timelines, entity_map, get_chapter_slug('timelines', language))
        if timelines_section:
            add_section(timelines_section, output_lines)
    
    # Remove the generic section rendering that causes duplication
    # The sections above handle all known entity types
    
    output_lines.append('---')
    output_lines.append(f"## {get_ui_text('generation_settings', language)}\n")
    output_lines.append(f"- **{get_ui_text('private_entities_display', language)}:** {get_ui_text('yes' if include_private else 'no', language)}\n")
    if not output_lines:
        return ''
    result = '\n'.join(output_lines)
    return result 