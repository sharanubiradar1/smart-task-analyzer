# 🎯 Smart Task Analyzer

An intelligent task management system that scores and prioritizes tasks based on multiple factors including urgency, importance, effort, and dependencies.

## 📋 Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
- [Algorithm Explanation](#algorithm-explanation)
- [Design Decisions](#design-decisions)
- [Time Breakdown](#time-breakdown)
- [Testing](#testing)
- [Future Improvements](#future-improvements)

## ✨ Features

### Core Features
- **Multi-Factor Priority Scoring**: Analyzes tasks based on urgency, importance, effort, and dependencies
- **Multiple Strategies**: Choose between Smart Balance, Fastest Wins, High Impact, or Deadline Driven prioritization
- **Circular Dependency Detection**: Automatically detects and reports circular dependencies
- **Top 3 Suggestions**: Get intelligent recommendations on which tasks to tackle first
- **Dual Input Methods**: Manual form entry or bulk JSON import
- **Real-time Analysis**: Instant priority calculations with detailed explanations
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

### Edge Case Handling
- ✅ Overdue tasks (weighted appropriately)
- ✅ Missing or invalid data validation
- ✅ Circular dependency detection
- ✅ Self-dependency prevention
- ✅ Unreasonable time estimates (>1000 hours)
- ✅ Duplicate dependencies

## 🛠️ Tech Stack

**Backend:**
- Python 3.8+
- Django 4.2.7
- Django REST Framework 3.14.0
- Django CORS Headers 4.3.0

**Frontend:**
- HTML5
- CSS3 (Custom, no frameworks)
- Vanilla JavaScript (ES6+)

**Testing:**
- Django TestCase
- 15+ unit tests covering edge cases

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd task-analyzer