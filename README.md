# Kun.uz Article Parser

This parser extracts articles from the [Kun.uz authored page](https://kun.uz/authored) and saves them as text files in the `news` folder.

## How It Works

The parser uses a sophisticated approach to extract all articles from the Kun.uz authored page:

1. **Dynamic Content Loading**: The parser navigates to https://kun.uz/authored and dynamically loads content by finding and interacting with "Load more" buttons or pagination elements.

2. **Progressive Page Processing**: Instead of trying to load all content at once, the parser processes articles page by page, extracting content from each article as it discovers them.

3. **Duplicate Prevention**: The parser keeps track of all processed articles to avoid duplicates when loading multiple pages.

4. **Robust Element Detection**: The parser uses multiple strategies to find the "Load more" button or pagination elements:
   - Specific class names like `point-view__footer-btn`
   - Dynamic IDs containing `ias_trigger`
   - XPath expressions for various text variations of "Ko'proq yangiliklar"
   - Fallback to general class names and text content matching

5. **Content Extraction**: For each article, the parser extracts:
   - Title (from `h1.news-inner__content-title`)
   - Publication date (from `div.news-inner__content-stats`)
   - Author information (from `div.news-inner__author`)
   - Main content (from `div.news-inner__content-page`)

6. **Error Handling**: The parser includes robust error handling for network issues, connection timeouts, and content extraction failures.

## Key Features

- **Headless Browser Automation**: Uses Selenium WebDriver in headless mode for efficient scraping
- **Anti-Detection Measures**: Implements techniques to avoid bot detection
- **Graceful Error Recovery**: Continues processing even when individual articles fail
- **Duplicate Prevention**: Tracks processed articles to avoid saving duplicates
- **Configurable Delays**: Includes appropriate delays to respect the server
- **Comprehensive Logging**: Provides detailed output about the parsing process

## Technical Implementation

### Main Components

1. **setup_driver()**: Configures Chrome WebDriver with appropriate options for headless operation and anti-detection measures

2. **extract_article_content()**: Extracts content from individual article pages using BeautifulSoup

3. **save_article_to_file()**: Saves extracted content to text files in the `news` folder

4. **get_current_article_links()**: Extracts article links from the current page

5. **main()**: Orchestrates the entire parsing process

### Parsing Strategy

The parser uses a multi-step approach to find and click pagination elements:

1. First tries specific class names based on the page structure
2. Falls back to dynamic ID detection
3. Uses XPath expressions for various text variations
4. Tries common class names for pagination buttons
5. Finally searches all buttons for text containing pagination keywords

### Content Extraction Process

For each article, the parser:
1. Navigates to the article URL
2. Waits for the page to load
3. Parses the HTML with BeautifulSoup
4. Extracts title, date, author, and content
5. Formats the content into a structured text file
6. Saves the file to the `news` folder

## Requirements

- Python 3.7+
- Selenium WebDriver
- ChromeDriver
- BeautifulSoup4

## Installation

1. Install Python 3.7 or higher
2. Install required packages:
   ```bash
   pip install selenium beautifulsoup4
   ```
3. Download and install ChromeDriver compatible with your Chrome version

## Usage

Run the parser:
```bash
python parser.py
```

The parsed articles will be saved as individual text files in the `news` folder.

## Output Format

Each article is saved as a text file with the following structure:
```
Title: [Article Title]

Date: [Publication Date]

Author: [Author Name]

Content:
[Article content with paragraphs separated by blank lines]
```

## Current Status

The parser has successfully extracted and saved **more then 500 articles** from the Kun.uz authored page. It handles network connectivity issues gracefully and continues processing even when some articles fail to load.

## Error Handling

The parser includes comprehensive error handling:

- **Network Errors**: Implements retry logic with exponential backoff
- **Connection Timeouts**: Handles connection resets and timeouts gracefully
- **Missing Elements**: Continues processing when specific HTML elements are not found
- **File I/O Errors**: Reports errors when saving files but continues with other articles
- **User Interruption**: Gracefully handles Ctrl+C interruption

## Performance Considerations

- Uses two separate WebDriver instances (one for listing, one for extraction) to improve performance
- Implements appropriate delays between requests to avoid overwhelming the server
- Processes articles in batches to manage memory usage
- Stops after a reasonable number of pages to prevent infinite loops

## Limitations

- May be affected by changes to the Kun.uz website structure
- Dependent on the availability and stability of the target website
- May be subject to anti-bot measures implemented by the website
- Processing speed is limited by network latency and website response times

## Troubleshooting

If you encounter issues:

1. **Connection Errors**: Try running the parser again later when the server is less busy
2. **Missing Content**: Check if the website structure has changed
3. **Slow Performance**: Ensure you have a stable internet connection
4. **Driver Issues**: Verify ChromeDriver is properly installed and compatible with your Chrome version

The parser is designed to continue processing even when individual articles fail, so occasional errors won't stop the entire process.

Command to count the number of articles: `(Get-ChildItem -Path "news" -File).Count`