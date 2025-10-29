#!/bin/bash

# Navigate to project directory
cd /home/user23/Code/Projects/Predictive_Yield_Nexus || exit

# Initialize git in the directory if not already
if [ ! -d ".git" ]; then
  git init
fi

git status

# Add and commit changes
if [ -n "$(git status --porcelain)" ]; then
  git add .
  git commit -m "Initial commit after rebranding: Predictive Yield Nexus"
fi

# Set the local main branch
git branch -M main

# Add remote if not already added
if ! git remote | grep origin > /dev/null; then
  git remote add origin https://github.com/§§secret(GITHUB_USERNAME)/Predictive-Yield-Nexus.git
fi

# Push to GitHub
if git push -u origin main; then
  echo "Push to GitHub successful!"
else
  echo "Failed to push to GitHub. Please check your connection and try again."
fi
