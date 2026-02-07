# Applications Management - Quick Visual Guide

## 📊 Applications List Page

### URL: `/dashboard/applications/`

```
┌─────────────────────────────────────────────────────────────────┐
│                      Applications Dashboard                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Total   │  │  Under   │  │ Accepted │  │ Rejected │       │
│  │    15    │  │ Review 5 │  │     8    │  │     2    │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  🔍 Search & Filters                        [+ New Application]  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Search: [________________]  Status: [All Statuses ▼]    │  │
│  │ Competition: [All ▼]        Student: [All ▼]            │  │
│  │ From: [2024-01-01]          To: [2024-12-31]            │  │
│  │ Sort: [Newest First ▼]                                   │  │
│  │                                                           │  │
│  │ [Apply Filters]  [Reset]                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📝 Math Olympiad 2024                    [✅ Accepted]         │
│  #WON-2024-00123                                              → │
│  📍 Paris, France  |  📅 Mar 15, 2024  |  💰 $2,500             │
│  👤 John Smith (Student)  |  🕐 Submitted Feb 10, 2024          │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📝 Science Fair International            [⏰ Under Review]      │
│  #WON-2024-00124                                              → │
│  📍 Tokyo, Japan  |  📅 Apr 20, 2024  |  💰 $3,200              │
│  👤 Jane Doe (Student)  |  🕐 Submitted Feb 12, 2024             │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [← Previous]  Page 1 of 2  [Next →]                            │
│  Showing 1 to 10 of 15 applications                              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 📄 Application Detail Page

### URL: `/dashboard/applications/<uuid>/`

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back to Applications        Application 3 of 15              │
│                                 [← Previous] [Next →]            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Math Olympiad 2024                          [✅ Accepted]       │
│  Application #WON-2024-00123                                     │
│                                            Submitted: Feb 10, 2024│
│                                                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ 👤 Student   │ │ 📍 Destination│ │ 📅 Dates     │            │
│  │ John Smith   │ │ Paris, France │ │ Mar 15-20    │            │
│  │ john@ex.com  │ │               │ │ 5 days       │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [Details] [Documents (3)] [Travel Quote] [Notes]               │
│                                                                   │
│  ═══════════════════════════════════════════════════════════    │
│                                                                   │
│  📋 Competition Information                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Competition: Math Olympiad 2024                          │   │
│  │ Subject: Mathematics                                     │   │
│  │ Location: Paris, France                                  │   │
│  │ Start Date: March 15, 2024                              │   │
│  │ End Date: March 20, 2024                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  👤 Student Information                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Name: John Smith                                         │   │
│  │ Email: john@example.com                                  │   │
│  │ Phone: +1 234 567 8900                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  📞 Emergency Contact                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Name: Jane Smith                                         │   │
│  │ Phone: +1 234 567 8901                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ✉️ Motivation Letter                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ I am passionate about mathematics and eager to           │   │
│  │ represent my school at this prestigious competition...   │   │
│  │ [Full letter content...]                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 User Flows

### Student Flow:
```
1. Login → Dashboard
2. Click "Applications" in sidebar
3. See own applications only
4. Click on application to view details
5. Use Next/Previous to navigate between applications
```

### Parent Flow:
```
1. Login → Dashboard
2. Click "Applications" in sidebar
3. See all children's applications
4. Filter by specific child if needed
5. Click on application to view details
6. See which child the application belongs to
```

### School Flow:
```
1. Login → Dashboard
2. Click "Applications" in sidebar
3. See all students' applications
4. Filter by student, status, competition, etc.
5. Search by student name or application number
6. Click to view detailed application information
```

## 🔍 Search Examples

### Search by Application Number:
```
Search: "WON-2024-00123"
Result: Shows specific application
```

### Search by Student Name:
```
Search: "John Smith"
Result: Shows all applications for John Smith
```

### Search by Competition:
```
Search: "Math Olympiad"
Result: Shows all Math Olympiad applications
```

## 🎨 Status Colors

```
✅ Accepted         → Green badge
❌ Rejected         → Red badge  
⏰ Under Review     → Orange badge
📝 Submitted        → Blue badge
📋 Documents Pending → Yellow badge
📄 Draft            → Gray badge
⏸️ Waitlisted       → Purple badge
🚫 Withdrawn        → Gray badge
```

## 📱 Responsive Behavior

### Desktop (>1024px):
- 4 columns for statistics
- 3 columns for filters
- Full table layout for applications
- Side-by-side tabs

### Tablet (768px - 1024px):
- 2 columns for statistics
- 2 columns for filters
- Compact application cards
- Stacked tabs

### Mobile (<768px):
- 1 column layout throughout
- Collapsible filters
- Vertical application cards
- Swipeable tabs

## 🎯 Filter Combinations

### Example 1: Recent Accepted Applications
```
Status: Accepted
Sort: Newest First
Result: Shows recently accepted applications
```

### Example 2: Specific Student's Pending Applications
```
Student: John Smith
Status: Under Review, Submitted
Sort: Competition Name
Result: Shows John's pending applications alphabetically
```

### Example 3: Applications by Date Range
```
From: 2024-01-01
To: 2024-03-31
Status: All
Sort: Newest First
Result: Shows Q1 2024 applications
```

## 🚀 Quick Actions

### From List View:
- Click row → View details
- Click "New Application" → Start new application
- Change filters → Update list
- Navigate pages → View more applications

### From Detail View:
- Click "Back" → Return to list
- Click "Previous" → View previous application
- Click "Next" → View next application
- Switch tabs → View different information
- Download document → Get PDF/file

## 💡 Tips

1. **Quick Navigation**: Use Previous/Next buttons to review applications without going back to list

2. **Filter Persistence**: Filters remain active when viewing details and returning to list

3. **Search Tips**: 
   - Use partial names (e.g., "John" matches "John Smith")
   - Use application number for exact match
   - Use competition name to see all related applications

4. **Sorting**:
   - Default: Newest First
   - For review: Sort by Status
   - For planning: Sort by Start Date

5. **Mobile Usage**:
   - Swipe left/right in detail view to navigate
   - Tap to expand/collapse filters
   - Use hamburger menu for sidebar

## 🎓 User Type Differences

### Students See:
- ✅ Own applications only
- ✅ "New Application" button (if can apply)
- ✅ Subscription status
- ❌ Student filter (not needed)

### Parents See:
- ✅ All children's applications
- ✅ Student name in each row
- ✅ Student filter dropdown
- ✅ Which child each application belongs to

### Schools See:
- ✅ All students' applications
- ✅ Student name in each row
- ✅ Student filter dropdown
- ✅ Number of applications per student

## 📊 Statistics Meaning

- **Total**: All applications (any status)
- **Under Review**: Currently being evaluated
- **Accepted**: Successfully approved
- **Rejected**: Not approved

Excludes: Draft and Withdrawn applications from main stats

## 🔐 Security Notes

- Students can ONLY view their own applications
- Parents can ONLY view children's applications (created by them)
- Schools can ONLY view students' applications (created by them)
- All detail view access is permission-checked
- Unauthorized access redirects to list view with error message
