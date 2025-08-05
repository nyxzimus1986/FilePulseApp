#!/bin/bash
# GitHub Repository Setup Script for FilePulseApp
# Run this script after creating a repository on GitHub

echo "🚀 FilePulseApp - GitHub Repository Setup"
echo "========================================"
echo ""

# Check if GitHub CLI is installed
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI detected"
    echo ""
    echo "Creating repository on GitHub..."
    gh repo create FilePulseApp --public --description "A modern Python application for intelligent file system monitoring with advanced system/user change separation" --homepage "https://github.com/Nyxzimus1986/FilePulseApp"
    
    echo ""
    echo "Setting up remote and pushing..."
    git remote add origin https://github.com/Nyxzimus1986/FilePulseApp.git
    git branch -M main
    git push -u origin main
    
    echo ""
    echo "🎉 Repository created and pushed successfully!"
    echo "📍 Repository URL: https://github.com/Nyxzimus1986/FilePulseApp"
    
else
    echo "⚠️  GitHub CLI not found. Manual setup required."
    echo ""
    echo "📋 Manual Setup Instructions:"
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: FilePulseApp"
    echo "3. Description: A modern Python application for intelligent file system monitoring with advanced system/user change separation"
    echo "4. Make it public"
    echo "5. Don't initialize with README (we have one)"
    echo "6. Create repository"
    echo ""
    echo "Then run these commands:"
    echo "git remote add origin https://github.com/Nyxzimus1986/FilePulseApp.git"
    echo "git branch -M main"
    echo "git push -u origin main"
fi

echo ""
echo "📦 Next steps after repository is created:"
echo "1. Enable GitHub Pages (Settings > Pages > Deploy from branch: main)"
echo "2. Add repository topics: python, file-monitoring, gui, tkinter, watchdog"
echo "3. Enable Issues and Discussions in repository settings"
echo "4. Consider adding repository shields/badges"
echo "5. Star your own repository! ⭐"
echo ""
echo "🔧 Development workflow:"
echo "- Create feature branches: git checkout -b feature/new-feature"
echo "- Make changes and commit: git commit -m 'Add new feature'"
echo "- Push and create PR: git push origin feature/new-feature"
echo ""
echo "Happy coding! 🎉"
