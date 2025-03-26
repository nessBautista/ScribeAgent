from urllib.parse import urlparse

class NotionAPIUrlParser:
    """Utility for parsing Notion URLs."""
    
    @staticmethod
    def extract_id_from_url(url: str) -> str:
        """Extract the ID from a Notion URL."""
        try:
            parsed_url = urlparse(url)
        except Exception:
            raise ValueError("Not a valid Notion URL")
        
        # Check for valid Notion domain - must be exactly notion.so
        valid_domains = ["notion.so", "www.notion.so"]
        if not any(parsed_url.netloc == domain for domain in valid_domains):
            raise ValueError("Not a valid Notion URL")
        
        # Remove trailing slash and split path
        path = parsed_url.path.strip("/")
        if not path:
            raise ValueError("Could not extract ID from URL")
            
        # The ID is the part after the last dash in the path
        path_parts = path.split("-")
        
        if len(path_parts) > 1:
            return path_parts[-1].split("?")[0]  # Remove query params if present
        elif len(path_parts) == 1:
            return path_parts[0].split("?")[0]  # Remove query params if present
        else:
            raise ValueError("Could not extract ID from URL")