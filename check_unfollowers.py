#!/usr/bin/env python3
"""
Instagram Unfollowers Checker

This script checks who you follow on Instagram but who doesn't follow you back.
It accepts HTML or JSON files containing Instagram followers and following data.
"""

import json
import sys
import os
import re
from typing import Set, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup


# Constants
CONTENT_DETECTION_BYTES = 200
EXCLUDED_DOMAINS = ['instagram.com', 'www.instagram.com']


def is_valid_instagram_username(username: str) -> bool:
    """
    Validate Instagram username format.
    
    Instagram usernames must:
    - Be 1-30 characters long
    - Contain only alphanumeric characters, dots, and underscores
    - Not end with a dot
    
    Args:
        username: Username to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not username or len(username) > 30:
        return False
    # Instagram username pattern: alphanumeric, dots, underscores, not ending with dot
    pattern = r'^[a-zA-Z0-9._]+$'
    if not re.match(pattern, username):
        return False
    if username.endswith('.'):
        return False
    return True


def parse_json_file(filepath: str) -> Optional[Set[str]]:
    """
    Parse JSON file and extract usernames.
    
    Instagram JSON exports typically have structures like:
    - List of objects with 'string_list_data' containing username info
    - Direct list of usernames
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Set of usernames (lowercase) or None if parsing fails
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        usernames = set()
        
        # Handle different JSON structures
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    # Instagram export format: relationships_followers/following
                    if 'string_list_data' in item:
                        for user_data in item['string_list_data']:
                            if 'value' in user_data:
                                usernames.add(user_data['value'].lower())
                    # Alternative format: direct username field
                    elif 'username' in item:
                        usernames.add(item['username'].lower())
                elif isinstance(item, str):
                    # Direct list of usernames
                    usernames.add(item.lower())
        elif isinstance(data, dict):
            # Handle dict with followers/following keys
            if 'followers' in data:
                usernames.update(extract_usernames_from_value(data['followers']))
            elif 'following' in data:
                usernames.update(extract_usernames_from_value(data['following']))
        
        return usernames
    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        print(f"Error parsing JSON file {filepath}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error parsing JSON file {filepath}: {e}", file=sys.stderr)
        return None


def extract_usernames_from_value(value) -> Set[str]:
    """
    Extract usernames from various value types.
    
    Args:
        value: Could be list, dict, or string
        
    Returns:
        Set of lowercase usernames
    """
    usernames = set()
    if isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                usernames.add(item.lower())
            elif isinstance(item, dict) and 'username' in item:
                usernames.add(item['username'].lower())
    elif isinstance(value, str):
        usernames.add(value.lower())
    return usernames


def parse_html_file(filepath: str) -> Optional[Set[str]]:
    """
    Parse HTML file and extract usernames using BeautifulSoup.
    
    Instagram HTML exports typically contain usernames in links or specific elements.
    
    Args:
        filepath: Path to HTML file
        
    Returns:
        Set of usernames (lowercase) or None if parsing fails
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        usernames = set()
        
        # Look for Instagram username patterns in links
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if not href:
                continue
            
            # Properly parse and validate Instagram profile links
            try:
                parsed = urlparse(href)
                # Check if it's a legitimate Instagram domain
                if parsed.netloc in ['www.instagram.com', 'instagram.com']:
                    # Extract username from path
                    path = parsed.path.strip('/').split('/')
                    if path and path[0]:
                        username = path[0]
                        if is_valid_instagram_username(username):
                            usernames.add(username.lower())
            except Exception:
                # Skip malformed URLs
                continue
        
        # Also look for text that might contain usernames
        # Instagram usernames are often in specific tags or classes
        for element in soup.find_all(['span', 'div', 'p']):
            text = element.get_text().strip()
            # Validate username format (alphanumeric, dots, underscores)
            if text and text.startswith('@'):
                username = text[1:].strip()
                if username and is_valid_instagram_username(username):
                    usernames.add(username.lower())
        
        return usernames if usernames else None
    except FileNotFoundError:
        print(f"Error: File {filepath} not found", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error parsing HTML file {filepath}: {e}", file=sys.stderr)
        return None


def parse_file(filepath: str) -> Optional[Set[str]]:
    """
    Parse file (JSON or HTML) and extract usernames.
    
    Args:
        filepath: Path to file
        
    Returns:
        Set of usernames (lowercase) or None if parsing fails
    """
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} does not exist", file=sys.stderr)
        return None
    
    # Determine file type by extension
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.json':
        return parse_json_file(filepath)
    elif ext in ['.html', '.htm']:
        return parse_html_file(filepath)
    else:
        # Try to detect file type by content
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read(CONTENT_DETECTION_BYTES)
                content_stripped = content.strip()
                content_lower = content.lower()
                
                # Check for JSON format
                if content_stripped.startswith(('{', '[')):
                    return parse_json_file(filepath)
                # Check for HTML format (more specific patterns)
                elif content_stripped.startswith(('<!DOCTYPE', '<html', '<HTML')) or \
                     ('<html>' in content_lower or '<!doctype html>' in content_lower):
                    return parse_html_file(filepath)
        except Exception:
            pass
        
        print(f"Error: Unable to determine file type for {filepath}", file=sys.stderr)
        return None


def find_unfollowers(followers_file: str, following_file: str) -> Set[str]:
    """
    Find users you follow who don't follow you back.
    
    Args:
        followers_file: Path to file containing your followers
        following_file: Path to file containing users you follow
        
    Returns:
        Set of usernames who don't follow you back
    """
    followers = parse_file(followers_file)
    following = parse_file(following_file)
    
    if followers is None:
        print(f"Failed to parse followers file: {followers_file}", file=sys.stderr)
        return set()
    
    if following is None:
        print(f"Failed to parse following file: {following_file}", file=sys.stderr)
        return set()
    
    # Find users in following but not in followers
    unfollowers = following - followers
    
    return unfollowers


def main():
    """Main function to run the unfollowers checker."""
    if len(sys.argv) != 3:
        print("Usage: python check_unfollowers.py <followers_file> <following_file>")
        print("\nExample:")
        print("  python check_unfollowers.py followers.json following.json")
        print("  python check_unfollowers.py followers.html following.html")
        print("\nAccepts HTML or JSON files containing Instagram followers and following data.")
        sys.exit(1)
    
    followers_file = sys.argv[1]
    following_file = sys.argv[2]
    
    print(f"Parsing followers from: {followers_file}")
    print(f"Parsing following from: {following_file}")
    print()
    
    unfollowers = find_unfollowers(followers_file, following_file)
    
    if unfollowers:
        print(f"Found {len(unfollowers)} users who don't follow you back:\n")
        for username in sorted(unfollowers):
            print(f"  - {username}")
    else:
        print("Great! Everyone you follow also follows you back!")


if __name__ == "__main__":
    main()
