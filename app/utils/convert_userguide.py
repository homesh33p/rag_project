#!/usr/bin/env python3
"""
Script to convert userguide_v1.md to CSV format for embedding in the RAG system.
"""
import re
import csv
import os
import sys
from pathlib import Path

def slugify(text):
    """Convert text to a URL-friendly format."""
    # Replace spaces with hyphens
    slug = text.lower().replace(' ', '-')
    
    # Remove special characters
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    
    # Remove multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    
    return slug

def clean_content(content):
    """Clean markdown content by removing code blocks and other formatting."""
    # Remove code blocks
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    
    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    # Replace multiple newlines with a single newline
    content = re.sub(r'\n\s*\n', '\n\n', content)
    
    # Replace double quotes with two single quotes (CSV escape)
    content = content.replace('"', '""')
    
    return content.strip()

def markdown_to_csv(input_path, output_path):
    """
    Convert a markdown file to CSV format with the following columns:
    - headingTrace: The heading/title of the section
    - pageTrace: Hierarchical path showing document structure
    - page_id: URL-friendly identifier for the page
    - section_id: Identifier for the section
    - content: The main text content
    - enhancedContent: Enhanced version with additional context
    """
    # Read the markdown file
    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Regular expressions to match headings
    h1_pattern = r'^# (.+?)$'
    h2_pattern = r'^## (.+?)$'
    h3_pattern = r'^### (.+?)$'
    h4_pattern = r'^#### (.+?)$'
    
    # Find all headings with their positions
    h1_matches = [(m.group(1), m.start()) for m in re.finditer(h1_pattern, md_content, re.MULTILINE)]
    h2_matches = [(m.group(1), m.start()) for m in re.finditer(h2_pattern, md_content, re.MULTILINE)]
    h3_matches = [(m.group(1), m.start()) for m in re.finditer(h3_pattern, md_content, re.MULTILINE)]
    h4_matches = [(m.group(1), m.start()) for m in re.finditer(h4_pattern, md_content, re.MULTILINE)]
    
    # Combine all headings with their levels and positions
    all_headings = [(1, title, pos) for title, pos in h1_matches]
    all_headings.extend([(2, title, pos) for title, pos in h2_matches])
    all_headings.extend([(3, title, pos) for title, pos in h3_matches])
    all_headings.extend([(4, title, pos) for title, pos in h4_matches])
    
    # Sort by position in document
    all_headings.sort(key=lambda x: x[2])
    
    # Extract content between headings
    sections = []
    for i in range(len(all_headings)):
        level, title, start_pos = all_headings[i]
        
        # Find heading text start position (after the heading line)
        heading_line_end = md_content.find("\n", start_pos) + 1
        
        # Find content end position (next heading or end of file)
        if i < len(all_headings) - 1:
            end_pos = all_headings[i+1][2]
        else:
            end_pos = len(md_content)
        
        # Extract content
        content = md_content[heading_line_end:end_pos].strip()
        
        # Clean content
        content = clean_content(content)
        
        sections.append((level, title, content, start_pos))
    
    # Generate CSV rows
    csv_rows = []
    document_title = "RAG System User Guide"  # Root title
    current_path = [document_title, None, None, None, None]  # Track headings at each level (0-4)
    
    for level, title, content, _ in sections:
        # Update current path (levels are 1-4, but array is 0-indexed)
        current_path[level] = title
        for i in range(level+1, 5):
            if i < len(current_path):
                current_path[i] = None
        
        # Create page trace
        page_trace_parts = []
        for i in range(level+1):
            if current_path[i] is not None:
                page_trace_parts.append(current_path[i])
        
        page_trace = "<_dot_>".join(page_trace_parts)
        
        # Create IDs
        section_id = slugify(title)
        page_id = section_id
        
        # Create enhanced content with context
        context_path = " > ".join(page_trace_parts[:-1]) if len(page_trace_parts) > 1 else ""
        enhanced_content = f"This content is about '{title}'"
        if context_path:
            enhanced_content += f" within the section '{context_path}'"
        enhanced_content += f". {content}"
        
        # Add to CSV rows
        csv_rows.append({
            'headingTrace': title,
            'pageTrace': page_trace,
            'page_id': page_id,
            'section_id': section_id,
            'content': content,
            'enhancedContent': enhanced_content
        })
    
    # Write to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['headingTrace', 'pageTrace', 'page_id', 'section_id', 'content', 'enhancedContent']
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(csv_rows)
    
    return len(csv_rows)

def main():
    """Convert the userguide markdown file to CSV format"""
    # Define input and output paths
    project_root = Path(__file__).parent.parent.parent
    input_file = project_root / "app" / "embeddings" / "userguide_v1.md"
    output_file = project_root / "app" / "embeddings" / "userguide_v1.csv"
    
    # Ensure the input file exists
    if not input_file.exists():
        print(f"Error: Input file {input_file} does not exist.")
        sys.exit(1)
    
    print(f"Converting {input_file} to {output_file}...")
    
    # Convert the markdown to CSV
    section_count = markdown_to_csv(input_file, output_file)
    
    print(f"Conversion complete! Created {output_file} with {section_count} sections.")

if __name__ == "__main__":
    main()