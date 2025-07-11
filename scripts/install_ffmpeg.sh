#!/bin/bash

# FFmpeg Installation Script for AI Video Generation
# This script detects your OS and installs FFmpeg accordingly

echo "🎬 FFmpeg Installation Script for AI Video Generation"
echo "=================================================="

# Detect operating system
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "🐧 Detected Linux system"
    
    if command -v apt-get &> /dev/null; then
        echo "📦 Using apt package manager..."
        sudo apt update
        sudo apt install -y ffmpeg
        
    elif command -v yum &> /dev/null; then
        echo "📦 Using yum package manager..."
        sudo yum install -y epel-release
        sudo yum install -y ffmpeg ffmpeg-devel
        
    elif command -v dnf &> /dev/null; then
        echo "📦 Using dnf package manager..."
        sudo dnf install -y ffmpeg ffmpeg-devel
        
    elif command -v pacman &> /dev/null; then
        echo "📦 Using pacman package manager..."
        sudo pacman -S ffmpeg
        
    else
        echo "❌ Unsupported Linux distribution"
        echo "Please install FFmpeg manually from: https://ffmpeg.org/download.html"
        exit 1
    fi
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "🍎 Detected macOS system"
    
    if command -v brew &> /dev/null; then
        echo "📦 Using Homebrew..."
        brew install ffmpeg
    else
        echo "❌ Homebrew not found"
        echo "Please install Homebrew first: https://brew.sh/"
        echo "Then run: brew install ffmpeg"
        exit 1
    fi
    
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows
    echo "🪟 Detected Windows system"
    
    if command -v choco &> /dev/null; then
        echo "📦 Using Chocolatey..."
        choco install ffmpeg
    else
        echo "❌ Chocolatey not found"
        echo "Please install FFmpeg manually:"
        echo "1. Download from: https://ffmpeg.org/download.html#build-windows"
        echo "2. Extract to C:\\ffmpeg"
        echo "3. Add C:\\ffmpeg\\bin to your PATH environment variable"
        echo "Or install Chocolatey and run: choco install ffmpeg"
        exit 1
    fi
    
else
    echo "❌ Unsupported operating system: $OSTYPE"
    echo "Please install FFmpeg manually from: https://ffmpeg.org/download.html"
    exit 1
fi

# Verify installation
echo ""
echo "🔍 Verifying FFmpeg installation..."

if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg installed successfully!"
    ffmpeg -version | head -1
    
    echo ""
    echo "🧪 Testing FFmpeg with a simple command..."
    
    # Create a test video
    ffmpeg -f lavfi -i testsrc=duration=1:size=320x240:rate=1 -y test_output.mp4 2>/dev/null
    
    if [ -f "test_output.mp4" ]; then
        echo "✅ FFmpeg test successful!"
        rm test_output.mp4
    else
        echo "⚠️  FFmpeg installed but test failed"
    fi
    
else
    echo "❌ FFmpeg installation failed"
    echo "Please try installing manually from: https://ffmpeg.org/download.html"
    exit 1
fi

echo ""
echo "🎉 FFmpeg setup complete!"
echo "Your AI video generation system can now create better mock videos."
