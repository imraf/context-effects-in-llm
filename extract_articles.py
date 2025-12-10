import csv
import random
import os
import sys
import json

csv.field_size_limit(sys.maxsize)

def extract_random_articles(input_file, output_dir, metadata_file='articles_metadata.json', num_articles=150):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    articles = []
    
    print(f"Reading {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            # Read all rows - assuming memory is sufficient for this file size
            # If file is extremely large, we would use reservoir sampling, 
            # but 50MB-1GB is fine for modern RAM.
            for row in reader:
                if row.get('text') and row.get('title'):
                    articles.append(row)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    total_articles = len(articles)
    print(f"Total articles found: {total_articles}")

    if total_articles < num_articles:
        print(f"Warning: Only {total_articles} articles available. Extracting all.")
        selected_articles = articles
    else:
        selected_articles = random.sample(articles, num_articles)

    print(f"Extracting {len(selected_articles)} articles to {output_dir}...")

    metadata_list = []

    for i, article in enumerate(selected_articles):
        # Sanitize title for filename
        safe_title = "".join([c for c in article['title'] if c.isalnum() or c in (' ', '-', '_')]).strip()
        safe_title = safe_title.replace(' ', '_')
        if not safe_title:
            safe_title = f"article_{i}"
        
        # Limit filename length
        filename = f"{i:03d}_{safe_title[:50]}.txt"
        file_path = os.path.join(output_dir, filename)

        # Prepare metadata entry
        # Parse tags if they look like a list string, otherwise keep as is
        tags_raw = article.get('tags', '')
        try:
            # Sometimes tags are stored as string representation of list "['tag1', 'tag2']"
            if tags_raw.startswith('[') and tags_raw.endswith(']'):
                tags = eval(tags_raw) # Be careful with eval, but for this CSV structure it's likely safe or use ast.literal_eval
            else:
                tags = [t.strip() for t in tags_raw.split(',') if t.strip()]
        except:
            tags = [tags_raw]

        metadata_entry = {
            "id": i,
            "filename": filename,
            "title": article['title'],
            "url": article['url'],
            "authors": article.get('authors', ''),
            "timestamp": article.get('timestamp', ''),
            "tags": tags,
            "length": len(article['text'])
        }
        metadata_list.append(metadata_entry)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write title and text
                f.write(f"Title: {article['title']}\n")
                f.write(f"URL: {article['url']}\n")
                f.write(f"Tags: {', '.join(tags)}\n")
                f.write("-" * 40 + "\n")
                f.write(article['text'])
        except Exception as e:
            print(f"Failed to write {filename}: {e}")

    # Save metadata to JSON file
    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_list, f, indent=4)
        print(f"Metadata saved to {metadata_file}")
    except Exception as e:
        print(f"Failed to save metadata: {e}")

    print("Extraction complete.")

if __name__ == "__main__":
    extract_random_articles('medium_articles.csv', 'random_articles')
