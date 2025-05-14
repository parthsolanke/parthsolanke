import os
from xml.etree import ElementTree
from typing import Dict, List
from utils.config import setup_logger

class SVGManager:
    def __init__(self, file_paths: List[str]):
        self.file_paths = []
        self.logger = setup_logger("SVGManager")
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                self.file_paths.append(file_path)
            else:
                self.logger.warning(f"SVG file not found: {file_path}")

    def _find_or_create_text(self, root, x, y, fill, font_size=None, font_weight=None, font_family=None) -> ElementTree.Element:
        for text_elem in root.findall('.//{http://www.w3.org/2000/svg}text'):
            if text_elem.get('x') == str(x) and text_elem.get('y') == str(y):
                return text_elem
                
        text_elem = ElementTree.SubElement(root, '{http://www.w3.org/2000/svg}text')
        text_elem.set('x', str(x))
        text_elem.set('y', str(y))
        text_elem.set('fill', fill)
        if font_size:
            text_elem.set('font-size', str(font_size))
        if font_weight:
            text_elem.set('font-weight', str(font_weight))
        if font_family:
            text_elem.set('font-family', font_family)
        return text_elem

    def _remove_text_by_y(self, root, y_values: List[str]):
        for parent in root.iter():
            for elem in list(parent):
                if elem.tag.endswith('text') and elem.get('y') in y_values:
                    parent.remove(elem)

    def _update_text(self, y: int, text: str, file_path: str, fill: str) -> bool:
        """
        Update text in an SVG file at a specific y-coordinate.
        
        Args:
            y: Y-coordinate of the text element
            text: New text content
            file_path: Path to the SVG file
            fill: Fill color for the text
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            tree = ElementTree.parse(file_path)
            root = tree.getroot()
            
            # Find the text element at the specified y-coordinate
            text_elem = None
            for elem in root.findall('.//{http://www.w3.org/2000/svg}text'):
                if elem.get('y') == str(y):
                    text_elem = elem
                    break
            
            if text_elem is None:
                # Create new text element if it doesn't exist
                text_elem = ElementTree.SubElement(root, '{http://www.w3.org/2000/svg}text')
                text_elem.set('x', '10')  # Default x position
                text_elem.set('y', str(y))
                text_elem.set('fill', fill)
                text_elem.set('font-family', 'Arial, sans-serif')
                text_elem.set('font-size', '14')
            
            # Update the text content
            text_elem.text = text
            
            # Save the updated SVG file
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating text in {file_path}: {str(e)}")
            return False

    def update_uptime(self, uptime_data: Dict):
        months_text = 'month' if uptime_data['months'] == 1 else 'months'
        days_text = 'day' if uptime_data['days'] == 1 else 'days'
        uptime_text = (
            f"Uptime: {uptime_data['years']} years, {uptime_data['months']} {months_text}, "
            f"{uptime_data['days']} {days_text}  ({uptime_data['total_days']}d, "
            f"{uptime_data['life_percentage']}%, {uptime_data['years_rounded']}y)"
        )
        
        success = True
        for file_path in self.file_paths:
            try:
                if self._update_text(56, uptime_text, file_path, '#4B5563'):
                    self.logger.info(f"Successfully updated uptime in {file_path}")
                else:
                    success = False
            except Exception as e:
                self.logger.error(f"Error updating uptime in {file_path}: {str(e)}")
                success = False
                
        if success:
            self.logger.info("Successfully updated uptime information in all SVG files")

    def update_github_stats(self, stats: Dict):
        stats_text = (
            f"GitHub: Repos: {stats['public_repos']} | Followers: {stats['followers']} | Stars: {stats['stars']} | "
            f"Contributed: {stats['contributed']} | Commits: {stats['commits']} | "
            f"Merged PRs: {stats['prs_merged']} ({stats['prs_merged_percentage']})"
        )
        
        success = True
        for file_path in self.file_paths:
            try:
                if self._update_text(84, stats_text, file_path, '#4B5563'):
                    self.logger.info(f"Successfully updated GitHub stats in {file_path}")
                else:
                    success = False
            except Exception as e:
                self.logger.error(f"Error updating GitHub stats in {file_path}: {str(e)}")
                success = False
                
        if success:
            self.logger.info("Successfully updated GitHub stats in all SVG files")
