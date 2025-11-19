import os
import time
import re
from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

def setup_driver():
    """Setup Chrome WebDriver with options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Make it more undetectable
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Suppress logging
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    
    # Set navigator.webdriver to undefined
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
    
    return driver

def extract_article_content(driver, url):
    """Extract content from a kun.uz article page"""
    try:
        print(f"Extracting content from: {url}")
        
        retries = 3
        while retries > 0:
            try:
                driver.get(url)
                time.sleep(5)
                break
            except Exception as e:
                print(f"Error loading page (attempt {4-retries}/3): {str(e)}")
                retries -= 1
                if retries == 0:
                    print(f"Failed to load {url} after 3 attempts")
                    return None
                print("Waiting before retry...")
                time.sleep(10)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        title_elem = soup.find('h1', class_='news-inner__content-title')
        title = title_elem.get_text(strip=True) if title_elem else "No title found"
        
        content_div = soup.find('div', class_='news-inner__content-page')
        content_text = ""
        
        if content_div:
            for script in content_div(["script", "style"]):
                script.decompose()
            
            paragraphs = content_div.find_all('p')
            content_parts = []
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 10:
                    content_parts.append(text)
            
            content_text = "\n\n".join(content_parts)
        
        author_elem = soup.find('div', class_='news-inner__author')
        author = ""
        if author_elem:
            author_link = author_elem.find('a')
            author = author_link.get_text(strip=True) if author_link else author_elem.get_text(strip=True)
        
        date_elem = soup.find('div', class_='news-inner__content-stats')
        date = ""
        if date_elem:
            date_span = date_elem.find('span')
            date = date_span.get_text(strip=True) if date_span else ""
        
        full_content = f"Title: {title}\n\n"
        if date:
            full_content += f"Date: {date}\n\n"
        if author:
            full_content += f"Author: {author}\n\n"
        full_content += f"Content:\n{content_text}"
        
        return full_content if len(content_text.strip()) > 50 else None
        
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"Error extracting content from {url}: {str(e)}")
        return None

def save_article_to_file(content, url, folder_path):
    """Save article content to a text file"""
    try:
        article_id = url.split('/')[-1]
        filename = f"{article_id}.txt"
        file_path = os.path.join(folder_path, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Saved article: {filename}")
        return True
    except Exception as e:
        print(f"Error saving article {url}: {str(e)}")
        return False

def get_current_article_links(driver):
    """Extract current article links from the page source"""
    # Scroll to bottom to ensure all content is loaded
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    current_links = []
    news_links = soup.find_all('a', href=True)
    
    for a_tag in news_links:
        href = str(a_tag['href'])
        if re.match(r'^/news/\d{4}/\d{2}/\d{2}/', href):
            full_url = f"https://kun.uz{href}" if not href.startswith('https://') else href
            current_links.append(full_url)
        elif href.startswith('https://kun.uz/news/') and re.search(r'/news/\d{4}/\d{2}/\d{2}/', href):
            current_links.append(href)
    
    return set(current_links)

def main():
    """Main function to run the parser"""
    print("Starting kun.uz article parser for authored page...")
    
    folder_path = "news"
    os.makedirs(folder_path, exist_ok=True)
    
    list_driver = setup_driver()
    extract_driver = setup_driver()
    
    try:
        current_url = "https://kun.uz/authored"
        list_driver.get(current_url)
        time.sleep(5)
        
        all_links = set()
        page = 0
        max_pages = 100
        no_new_count = 0
        max_no_new = 3
        
        print("Starting to load and process articles page by page...")
        
        while page < max_pages:
            page += 1
            print(f"Processing page {page}: {current_url}")
            
            current_links = get_current_article_links(list_driver)
            new_links = current_links - all_links
            
            if not new_links:
                print(f"No new articles found on page {page}.")
                no_new_count += 1
                if no_new_count >= max_no_new:
                    print("No new articles after multiple attempts. Stopping.")
                    break
                else:
                    time.sleep(5)  # Wait a bit before trying again
                    continue
            else:
                no_new_count = 0
            
            print(f"Found {len(new_links)} new articles on page {page}")
            all_links.update(new_links)
            
            processed_count = 0
            failed_count = 0
            for i, url in enumerate(sorted(new_links), 1):
                try:
                    print(f"\nProcessing article {i}/{len(new_links)} on page {page}: {url}")
                    content = extract_article_content(extract_driver, url)
                    if content:
                        if save_article_to_file(content, url, folder_path):
                            processed_count += 1
                    else:
                        print(f"Failed to extract content for {url}")
                        failed_count += 1
                    time.sleep(3)
                except Exception as e:
                    print(f"Unexpected error processing {url}: {str(e)}")
                    failed_count += 1
            
            print(f"Page {page} processed: {processed_count} successful, {failed_count} failed")
            
            # Find the next element
            next_elem = None
            
            # Try specific class from screenshot
            try:
                next_elem = WebDriverWait(list_driver, 10).until(
                    ec.element_to_be_clickable((By.CLASS_NAME, "point-view__footer-btn"))
                )
            except Exception as e:
                print(e)
            
            if not next_elem:
                # Try dynamic ID
                try:
                    next_elem = WebDriverWait(list_driver, 10).until(
                        ec.element_to_be_clickable((By.XPATH, "//div[contains(@id, 'ias_trigger')]/button"))
                    )
                except Exception as e:
                    print(e)

            
            if not next_elem:
                xpaths = [
                    '//button[contains(., "Ko\'proq yangiliklar")]',
                    '//button[contains(., "Ko‘proq yangiliklar")]',
                    '//button[contains(., "Ko’proq yangiliklar")]',
                    '//button[contains(., "Koʻproq yangiliklar")]',
                    '//button[contains(., "Ko\'proq maqolalar")]',
                    '//button[contains(., "Ko‘proq maqolalar")]',
                    '//button[contains(., "Ko’proq maqolalar")]',
                    '//button[contains(., "Koʻproq maqolalar")]',
                ]
                
                for xp in xpaths:
                    try:
                        next_elem = WebDriverWait(list_driver, 10).until(
                            ec.element_to_be_clickable((By.XPATH, xp))
                        )
                        break
                    except Exception as e:
                        print(e)
            
            if not next_elem:
                classes = ["point-view__footer-btn", "more-btn", "load-more", "load-more-btn", "btn-load-more", "more-news", "load-more__button"]
                for cls in classes:
                    try:
                        next_elem = WebDriverWait(list_driver, 10).until(
                            ec.element_to_be_clickable((By.CLASS_NAME, cls))
                        )
                        break
                    except Exception as e:
                        print(e)
            
            if not next_elem:
                elements = list_driver.find_elements(By.XPATH, "//button")
                for el in elements:
                    text = el.text.lower()
                    if any(word in text for word in ["ko'proq", "ko‘proq", "ko’proq", "koʻproq", "yana", "yangiliklar", "maqolalar", "more", "load"]):
                        next_elem = el
                        break
            
            if not next_elem:
                print("No more load more element found. Stopping.")
                break
            
            list_driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", next_elem)
            time.sleep(2)
            
            href = next_elem.get_attribute('href')
            if href and '?next=' in href:
                print(f"Navigating to next page via href: {href}")
                current_url = href if href.startswith('https://') else f"https://kun.uz/authored{href}"
                list_driver.get(current_url)
                time.sleep(10)  # Longer wait after navigation
            else:
                old_url = list_driver.current_url
                old_links_len = len(current_links)
                
                print("Clicking load more element")
                list_driver.execute_script("arguments[0].click();", next_elem)
                
                time.sleep(10)  # Longer sleep after click
                
                new_url = list_driver.current_url
                if new_url != old_url:
                    print(f"Navigated to new page via click: {new_url}")
                    current_url = new_url
                else:
                    print("URL did not change, assuming content appended.")
                    try:
                        WebDriverWait(list_driver, 60).until(
                            lambda d: len(get_current_article_links(d)) > old_links_len
                        )
                        print("New articles appended successfully.")
                    except TimeoutException:
                        print("Timeout waiting for new articles to append after 60 seconds. Stopping.")
                    except Exception as e:
                        print(e)
                
                time.sleep(5)
        
        print(f"Finished after {page} pages")
        print(f"Total unique articles processed: {len(all_links)}")
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        try:
            list_driver.quit()
            extract_driver.quit()
        except WebDriverException:
            print("Error closing WebDrivers")
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()

# Last page  https://kun.uz/authored?next=1703247560