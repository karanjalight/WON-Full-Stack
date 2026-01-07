# 🚀 Quick Image Download Links - WON Landing Page

## ⚡ Fastest Way to Get Started

### Method 1: Use the Python Script (Automated)
```bash
cd /path/to/won-fullstack
python3 download_images.py
```

### Method 2: Manual Download (Pick & Choose)

---

## 📸 Priority Images - Download First

### 1. HERO BACKGROUNDS (2 images minimum)

**Image 1**: Students Studying Together
- **Link**: https://unsplash.com/photos/people-sitting-down-near-table-with-assorted-laptop-computers-QckxruozjRg
- **Download**: Click "Download free" → Select "Original" → Save as `hero-2.jpg`

**Image 2**: University Classroom
- **Link**: https://unsplash.com/photos/people-sitting-on-chair-in-front-of-table-while-holding-pens-during-daytime-5fNmWej4tAA
- **Download**: Click "Download free" → Select "Original" → Save as `hero-3.jpg`

---

### 2. FEATURED COMPETITIONS (6 images)

**Mathematics**
- **Link**: https://unsplash.com/photos/person-writing-on-white-paper-5mZ_M06Fc9g
- **Save as**: `destinations/01.jpg`

**Physics**
- **Link**: https://unsplash.com/photos/books-on-brown-wooden-shelf-ue2AOtPPaWM
- **Save as**: `destinations/02.jpg`

**Chemistry**
- **Link**: https://unsplash.com/photos/person-holding-round-clear-container-XyNWXZpukPY
- **Save as**: `destinations/03.jpg`

**Biology**
- **Link**: https://unsplash.com/photos/person-looking-at-microscope-oMpAz-DN-9I
- **Save as**: `destinations/04.jpg`

**Informatics/Programming**
- **Link**: https://unsplash.com/photos/macbook-pro-on-black-textile-w7ZyuGYNpRQ
- **Save as**: `destinations/05.jpg`

**Pan-African Students**
- **Link**: https://unsplash.com/photos/woman-in-white-shirt-using-smartphone-rDEOVtE7vOs
- **Save as**: `destinations/06.jpg`

---

### 3. TUTORS SECTION (4 headshots)

**Professional Woman (Dr. Amina)**
- **Link**: https://unsplash.com/photos/woman-wearing-black-scoop-neck-long-sleeved-shirt-mEZ3PoFGs_k
- **Save as**: `team/09.jpg`

**Professional Man (Prof. Kwame)**
- **Link**: https://unsplash.com/photos/man-standing-near-white-wall-WNoLnJo7tS8
- **Save as**: `team/10.jpg`

**Professional Woman 2 (Dr. Fatima)**
- **Link**: https://unsplash.com/photos/woman-smiling-wearing-red-and-black-checkered-dress-shirt-7YVZYZeITc8
- **Save as**: `team/11.jpg`

**Professional Man 2 (Mr. David)**
- **Link**: https://unsplash.com/photos/man-in-red-polo-shirt-smiling-iFgRcqHznqg
- **Save as**: `team/12.jpg`

---

## 🌐 Direct Search Links (Browse & Download)

### General Student/Education Images
```
Unsplash - Students Studying:
https://unsplash.com/s/photos/students-studying

Unsplash - STEM Education:
https://unsplash.com/s/photos/stem-education

Unsplash - Competition:
https://unsplash.com/s/photos/student-competition

Unsplash - African Students:
https://unsplash.com/s/photos/african-students

Pexels - Students:
https://www.pexels.com/search/students/

Pexels - Competition:
https://www.pexels.com/search/student%20competition/
```

### Professional Portraits (Tutors)
```
Unsplash - Professional Portraits:
https://unsplash.com/s/photos/professional-portrait

Unsplash - Teacher:
https://unsplash.com/s/photos/teacher

Pexels - Professional Headshots:
https://www.pexels.com/search/professional%20headshot/
```

### Subject-Specific
```
Mathematics:
https://unsplash.com/s/photos/mathematics

Physics:
https://unsplash.com/s/photos/physics-lab

Chemistry:
https://unsplash.com/s/photos/chemistry

Biology:
https://unsplash.com/s/photos/biology-science

Programming/Coding:
https://unsplash.com/s/photos/coding
```

---

## 📥 Download Instructions

### On Unsplash:
1. Click the image link
2. Click "Download free" button (top right)
3. Select size (choose "Original" for best quality)
4. Image downloads to your Downloads folder
5. Move to appropriate folder in `assets/img/`

### On Pexels:
1. Click the image
2. Click green "Download" button
3. Choose "Original" size
4. Move to appropriate folder in `assets/img/`

---

## 📂 File Structure

After downloading, organize like this:
```
assets/img/
├── hero/
│   ├── hero-2.jpg
│   └── hero-3.jpg
├── destinations/
│   ├── 01.jpg
│   ├── 02.jpg
│   ├── 03.jpg
│   ├── 04.jpg
│   ├── 05.jpg
│   └── 06.jpg
├── tour/
│   ├── 01.jpg
│   ├── 02.jpg
│   └── ... (more competition images)
├── team/
│   ├── 09.jpg
│   ├── 10.jpg
│   ├── 11.jpg
│   └── 12.jpg
├── about/
│   └── 03.jpg
└── news/
    ├── news-11.jpg
    ├── news-12.jpg
    └── news-13.jpg
```

---

## ✨ Pro Tips

1. **Consistent Style**: Choose images with similar lighting/color tones
2. **Diversity**: Mix different ethnicities, genders, ages
3. **Authenticity**: Avoid overly staged stock photos
4. **Quality**: Download "Original" size, then compress
5. **Compression**: Use https://tinypng.com to reduce file size

---

## ⚙️ Image Optimization (After Download)

### Online (Easy):
1. Go to https://tinypng.com
2. Drag all downloaded images
3. Click "Download all" when complete
4. Replace original files

### CLI (Advanced):
```bash
# Install ImageMagick
sudo apt install imagemagick  # Ubuntu/Debian

# Resize and compress
for img in *.jpg; do
    convert "$img" -resize 1920x1080^ -quality 85 "optimized_$img"
done
```

---

## 🎯 Minimum Viable Images (MVP)

If you only have 10 minutes, download these:
1. ✅ 2 Hero backgrounds
2. ✅ 6 Featured competition images
3. ✅ 4 Tutor headshots

**Total**: 12 images = Fully functional landing page

---

## 📞 Need Help?

**Can't find right images?** Use these keywords:
- "diverse students learning"
- "african STEM education"
- "international student competition"
- "academic achievement"
- "professional educator portrait"

**License Questions?**
- Unsplash: Free for commercial use, no attribution required
- Pexels: Free for commercial use, no attribution required
- Pixabay: Free for commercial use, attribution appreciated

---

**Ready to go?** Start with the automated script or manual downloads above!














