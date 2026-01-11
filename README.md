# Instagram Unfollower Checker

A Python script that identifies Instagram users who you follow but who don't follow you back.

## Features

- Accepts both HTML and JSON files containing Instagram followers and following data
- Case-insensitive username matching
- Handles duplicates gracefully
- Error handling for invalid files
- Simple command-line interface

## Requirements

- Python 3
- BeautifulSoup4

## Installation

1. Clone this repository:
```bash
git clone https://github.com/krispandeya/instagram.git
cd instagram
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python check_unfollowers.py <followers_file> <following_file>
```

### Examples

With JSON files:
```bash
python check_unfollowers.py followers.json following.json
```

With HTML files:
```bash
python check_unfollowers.py followers.html following.html
```

### Getting Your Instagram Data

To use this script, you need to download your Instagram data:

1. Go to Instagram Settings → Security → Download Data
2. Request a download of your information
3. Once ready, download and extract the ZIP file
4. Find the `followers.json` and `following.json` files in the extracted folder
5. Run the script with these files

### Supported File Formats

**JSON Format:**
- Instagram's official data export format (with `string_list_data` structure)
- Simple list of username objects
- Dictionary with followers/following keys

**HTML Format:**
- HTML files containing Instagram profile links
- Usernames prefixed with @ symbol

## Output

The script will display:
- Number of users who don't follow you back
- List of usernames in alphabetical order

Example output:
```
Parsing followers from: followers.json
Parsing following from: following.json

Found 2 users who don't follow you back:

  - user4_unfollower
  - user5_unfollower
```

## Error Handling

The script gracefully handles:
- Missing files
- Invalid JSON/HTML syntax
- Duplicate usernames
- Various data formats

## License

MIT
