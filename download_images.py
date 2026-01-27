#!/usr/bin/env python3
"""
WON Landing Page - Image Download Helper
Downloads sample images from Unsplash for the landing page
"""

import os
import urllib.request
import ssl

# Disable SSL verification for downloads (if needed)
ssl._create_default_https_context = ssl._create_unverified_context

# Base directory for assets
ASSETS_DIR = "../assets/img"

# Sample high-quality Unsplash images (Direct download links)
# These are curated, free-to-use images relevant to WON
IMAGES = {
    # Hero Section - Students in academic settings
    "hero": [
        {
            "url": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1920&q=80",
            "filename": "hero-students-1.jpg",
            "description": "Students collaborating in university"
        },
        {
            "url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=1920&q=80",
            "filename": "hero-students-2.jpg",
            "description": "Students studying together"
        },
    ],
    
    # Featured Competitions - Subject-specific
    "destinations": [
        {
            "url": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800&q=80",
            "filename": "competition-math.jpg",
            "description": "Mathematics - equations on board"
        },
        {
            "url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=800&q=80",
            "filename": "competition-physics.jpg",
            "description": "Physics - laboratory equipment"
        },
        {
            "url": "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=800&q=80",
            "filename": "competition-chemistry.jpg",
            "description": "Chemistry - lab experiments"
        },
        {
            "url": "https://images.unsplash.com/photo-1530587191325-3db32d826c18?w=800&q=80",
            "filename": "competition-biology.jpg",
            "description": "Biology - microscope work"
        },
        {
            "url": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&q=80",
            "filename": "competition-informatics.jpg",
            "description": "Informatics - coding"
        },
        {
            "url": "https://images.unsplash.com/photo-1522661067900-ab829854a57f?w=800&q=80",
            "filename": "competition-panafrican.jpg",
            "description": "Pan-African - diverse students"
        },
    ],
    
    # Competitions/Tours - Students achieving
    "tour": [
        {
            "url": "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?w=600&q=80",
            "filename": "tour-01-imo.jpg",
            "description": "IMO - students with medals"
        },
        {
            "url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=600&q=80",
            "filename": "tour-02-ipho.jpg",
            "description": "IPhO - study group"
        },
        {
            "url": "https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=600&q=80",
            "filename": "tour-03-icho.jpg",
            "description": "IChO - chemistry students"
        },
        {
            "url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=600&q=80",
            "filename": "tour-04-ibo.jpg",
            "description": "IBO - biology research"
        },
        {
            "url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&q=80",
            "filename": "tour-05-ioi.jpg",
            "description": "IOI - programming"
        },
        {
            "url": "https://images.unsplash.com/photo-1543269865-cbf427effbad?w=600&q=80",
            "filename": "tour-06-pamo.jpg",
            "description": "PAMO - mathematics"
        },
    ],
    
    # About Section - Inspiring student
    "about": [
        {
            "url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=800&q=80",
            "filename": "about-student.jpg",
            "description": "Student studying - inspirational"
        },
    ],
    
    # Tutors - Professional educators
    "team": [
        {
            "url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&q=80",
            "filename": "tutor-01-amina.jpg",
            "description": "Dr. Amina - Mathematics"
        },
        {
            "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80",
            "filename": "tutor-02-kwame.jpg",
            "description": "Prof. Kwame - Physics"
        },
        {
            "url": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=400&q=80",
            "filename": "tutor-03-fatima.jpg",
            "description": "Dr. Fatima - Chemistry"
        },
        {
            "url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&q=80",
            "filename": "tutor-04-david.jpg",
            "description": "Mr. David - Informatics"
        },
    ],
    
    # News Section - Educational content
    "news": [
        {
            "url": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800&q=80",
            "filename": "news-01.jpg",
            "description": "Student success story"
        },
        {
            "url": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=800&q=80",
            "filename": "news-02.jpg",
            "description": "Competition preparation"
        },
        {
            "url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&q=80",
            "filename": "news-03.jpg",
            "description": "Team collaboration"
        },
    ],
}


def download_image(url, filepath, description):
    """Download a single image from URL to filepath"""
    try:
        print(f"Downloading: {description}")
        print(f"  URL: {url}")
        print(f"  Saving to: {filepath}")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Download the image
        urllib.request.urlretrieve(url, filepath)
        print(f"  ✓ Success!\n")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
        return False


def main():
    """Main download function"""
    print("=" * 60)
    print("WON Landing Page - Image Download Helper")
    print("=" * 60)
    print("\nThis script will download sample images from Unsplash")
    print("for your WON landing page.\n")
    print("NOTE: All images are from Unsplash and free to use.")
    print("=" * 60)
    print()
    
    # Track statistics
    total_images = 0
    successful_downloads = 0
    
    # Download images for each section
    for section, images in IMAGES.items():
        section_path = os.path.join(ASSETS_DIR, section)
        
        print(f"\n{'=' * 60}")
        print(f"Section: {section.upper()}")
        print(f"{'=' * 60}\n")
        
        for image_info in images:
            total_images += 1
            filepath = os.path.join(section_path, image_info["filename"])
            
            if download_image(image_info["url"], filepath, image_info["description"]):
                successful_downloads += 1
    
    # Print summary
    print("\n" + "=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"Total images: {total_images}")
    print(f"Successful: {successful_downloads}")
    print(f"Failed: {total_images - successful_downloads}")
    print("=" * 60)
    
    if successful_downloads > 0:
        print("\n✓ Images downloaded successfully!")
        print("\nNext steps:")
        print("1. Check the images in: ../assets/img/")
        print("2. Rename/move them to match your template structure")
        print("3. Refresh your browser at localhost:8000")
        print("\nFor more images, visit:")
        print("  - https://unsplash.com")
        print("  - https://pexels.com")
        print("  - https://pixabay.com")
    else:
        print("\n✗ No images were downloaded successfully.")
        print("Please check your internet connection and try again.")


if __name__ == "__main__":
    main()

















