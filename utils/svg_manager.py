import os
from xml.etree import ElementTree
from typing import Dict, List
from utils.config import setup_logger

# Register the SVG namespace
SVG_NS = "http://www.w3.org/2000/svg"
ElementTree.register_namespace('', SVG_NS)

class SVGManager:
    def __init__(self, file_paths: List[str]):
        self.file_paths = []
        self.logger = setup_logger("SVGManager")

        for file_path in file_paths:
            if os.path.exists(file_path):
                self.file_paths.append(file_path)
            else:
                self.logger.warning(f"SVG file not found: {file_path}")

    def _update_value_after_label(self, label: str, new_value: str, file_path: str) -> bool:
        try:
            tree = ElementTree.parse(file_path)
            root = tree.getroot()

            for text in root.findall(f'.//{{{SVG_NS}}}text'):
                tspans = list(text.findall(f'{{{SVG_NS}}}tspan'))
                for i, tspan in enumerate(tspans):
                    text_content = tspan.text.strip() if tspan.text else ""
                    if label in text_content:
                        for j in range(i + 1, len(tspans)):
                            next_tspan = tspans[j]
                            if next_tspan.get('class') == 'valueColor':
                                self.logger.info(f"Updating '{label}' in {file_path} to '{new_value}'")
                                next_tspan.text = new_value
                                tree.write(file_path, encoding='utf-8', xml_declaration=True)
                                return True
            self.logger.warning(f"Label '{label}' not found in {file_path}")
            return False

        except Exception as e:
            self.logger.error(f"Error updating label '{label}' in {file_path}: {str(e)}")
            return False
        
    def _update_nested_value_for_key(self, key: str, new_value: str, file_path: str) -> bool:
        try:
            tree = ElementTree.parse(file_path)
            root = tree.getroot()

            for text in root.findall(f'.//{{{SVG_NS}}}text'):
                for outer_tspan in text.findall(f'{{{SVG_NS}}}tspan'):
                    # Search inside nested tspans
                    inner_tspans = list(outer_tspan.findall(f'{{{SVG_NS}}}tspan'))
                    for i, inner_tspan in enumerate(inner_tspans):
                        if inner_tspan.text and key in inner_tspan.text:
                            # Try to update the next <tspan> with class 'valueColor'
                            for j in range(i + 1, len(inner_tspans)):
                                value_tspan = inner_tspans[j]
                                if value_tspan.get('class') == 'valueColor':
                                    self.logger.info(f"[NESTED] Updating '{key}' in {file_path} to '{new_value}'")
                                    value_tspan.text = new_value
                                    tree.write(file_path, encoding='utf-8', xml_declaration=True)
                                    return True
            self.logger.warning(f"[NESTED] Key '{key}' not found in {file_path}")
            return False

        except Exception as e:
            self.logger.error(f"Error updating nested key '{key}' in {file_path}: {str(e)}")
            return False
        
    def _replace_value_tspan_by_suffix(self, suffix: str, new_value: str, file_path: str) -> bool:
        try:
            tree = ElementTree.parse(file_path)
            root = tree.getroot()

            for text in root.findall(f'.//{{{SVG_NS}}}text'):
                for tspan in text.findall(f'{{{SVG_NS}}}tspan'):
                    if tspan.get('class') == 'valueColor' and tspan.text and tspan.text.strip().endswith(suffix):
                        self.logger.info(f"Replacing value ending with '{suffix}' in {file_path} to '{new_value}'")
                        tspan.text = new_value
                        tree.write(file_path, encoding='utf-8', xml_declaration=True)
                        return True

            self.logger.warning(f"No valueColor tspan ending with '{suffix}' found in {file_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error replacing value ending with '{suffix}' in {file_path}: {str(e)}")
            return False

    def update_uptime(self, uptime_data: Dict) -> bool:
        uptime_str = f"{uptime_data['years']} years, {uptime_data['months']} months, {uptime_data['days']} days"
        total_days = f"({uptime_data['total_days']}d)"
        life_percent = f"({uptime_data['life_percentage']}%)"
        rounded_years = f"({uptime_data['years_rounded']}y)"

        all_success = True
        for file_path in self.file_paths:
            all_success &= self._update_value_after_label("Uptime", uptime_str, file_path)
            all_success &= self._replace_value_tspan_by_suffix("d)", total_days, file_path)
            all_success &= self._replace_value_tspan_by_suffix("%)", life_percent, file_path)
            all_success &= self._replace_value_tspan_by_suffix("y)", rounded_years, file_path)
        return all_success

    def update_github_stats(self, stats: Dict) -> bool:
        all_success = True
        for file_path in self.file_paths:
            all_success &= self._update_value_after_label("Repos", str(stats['public_repos']), file_path)
            all_success &= self._update_value_after_label("Followers", str(stats['followers']), file_path)
            all_success &= self._update_value_after_label("Stars", str(stats['stars']), file_path)
            all_success &= self._update_nested_value_for_key("Contributed", str(stats['contributed']), file_path)
            all_success &= self._update_value_after_label("Commits", stats['commits'], file_path)
            all_success &= self._update_value_after_label("Merged PRs", f"{stats['prs_merged']} ({stats['prs_merged_percentage']})", file_path)
        return all_success
