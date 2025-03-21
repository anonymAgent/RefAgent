#!/bin/bash

set -u  # Treat unset variables as errors
set -e  # Exit on any command failure

# === CHECK ARGUMENTS ===
if [ "$#" -ne 2 ]; then
    echo "❌ Usage: $0 <org/repo-name> <tag>"
    echo "Example: $0 apache/maven v3.8.6"
    exit 1
fi

ORG_REPO="$1"
TAG="$2"

ORG=$(echo "$ORG_REPO" | cut -d'/' -f1)
REPO=$(echo "$ORG_REPO" | cut -d'/' -f2)

REPO_URL="https://github.com/$ORG_REPO.git"
BEFORE_PATH="projects/before/$REPO"
AFTER_PATH="projects/after/$REPO"

# === STEP 1: Clone specific tag only ===
if [ -d "$BEFORE_PATH" ]; then
    echo "📁 Project already exists at $BEFORE_PATH. Skipping clone."
else
    echo "📥 Cloning tag '$TAG' from $REPO_URL into $BEFORE_PATH..."
    mkdir -p "$(dirname "$BEFORE_PATH")"
    git clone --branch "$TAG" --depth 1 "$REPO_URL" "$BEFORE_PATH" || {
        echo "❌ Failed to clone tag '$TAG' from $REPO_URL"
        exit 1
    }
fi

# === STEP 2: Copy to 'after' directory ===
echo "📄 Copying project to $AFTER_PATH..."
rm -rf "$AFTER_PATH"
mkdir -p "$(dirname "$AFTER_PATH")"
cp -r "$BEFORE_PATH" "$AFTER_PATH"

# === STEP 3: Build using Maven ===
echo "🔧 Building project in $AFTER_PATH..."
cd "$AFTER_PATH"
if ! mvn clean install -DskipTests; then
    echo "❌ Maven build failed in $AFTER_PATH"
    exit 1
fi

echo "✅ Maven build succeeded!"

# === STEP 4: Run Python script with project name ===
cd ../../  # Assuming the shell script is at root level and refAgent is at ./refAgent/
echo "🚀 Running Python script for project: $REPO..."
python3 refAgent/RefAgent_main.py "$REPO"
