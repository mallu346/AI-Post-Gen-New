#!/usr/bin/env python3
"""
System requirements checker for AI Video Generation
"""

import sys
import subprocess
import importlib
import os

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} (Good)")
        return True
    else:
        print(f"  ⚠️  Python {version.major}.{version.minor}.{version.micro} (Recommended: 3.8+)")
        return False

def check_required_packages():
    """Check required Python packages"""
    print("📦 Checking required packages...")
    
    required_packages = [
        ('django', 'Django'),
        ('PIL', 'Pillow'),
        ('requests', 'requests'),
    ]
    
    optional_packages = [
        ('cv2', 'opencv-python'),
        ('numpy', 'numpy'),
        ('moviepy', 'moviepy'),
    ]
    
    missing_required = []
    missing_optional = []
    
    # Check required packages
    for package, name in required_packages:
        try:
            importlib.import_module(package)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} (REQUIRED)")
            missing_required.append(name)
    
    # Check optional packages
    for package, name in optional_packages:
        try:
            importlib.import_module(package)
            print(f"  ✅ {name} (optional)")
        except ImportError:
            print(f"  ⚠️  {name} (optional - for advanced video processing)")
            missing_optional.append(name)
    
    if missing_required:
        print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
        print("Install with: pip install " + " ".join(missing_required))
        return False
    
    if missing_optional:
        print(f"\n💡 Optional packages for better performance: {', '.join(missing_optional)}")
        print("Install with: pip install " + " ".join(missing_optional))
    
    return True

def check_ffmpeg():
    """Check FFmpeg installation"""
    print("🎬 Checking FFmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"  ✅ {version_line}")
            return True
        else:
            print("  ❌ FFmpeg not working properly")
            return False
    except FileNotFoundError:
        print("  ⚠️  FFmpeg not found (optional but recommended)")
        return False
    except Exception as e:
        print(f"  ❌ Error checking FFmpeg: {e}")
        return False

def check_disk_space():
    """Check available disk space"""
    print("💾 Checking disk space...")
    
    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        
        free_gb = free // (1024**3)
        total_gb = total // (1024**3)
        
        print(f"  📊 Available: {free_gb} GB / {total_gb} GB")
        
        if free_gb < 1:
            print("  ⚠️  Low disk space (less than 1 GB available)")
            print("     Video files can be large, consider freeing up space")
            return False
        elif free_gb < 5:
            print("  ⚠️  Limited disk space (less than 5 GB available)")
            return True
        else:
            print("  ✅ Sufficient disk space")
            return True
            
    except Exception as e:
        print(f"  ❌ Error checking disk space: {e}")
        return False

def check_django_setup():
    """Check Django project setup"""
    print("🔧 Checking Django setup...")
    
    # Check if manage.py exists
    if os.path.exists('manage.py'):
        print("  ✅ manage.py found")
    else:
        print("  ❌ manage.py not found - run from Django project root")
        return False
    
    # Check if we can import Django settings
    try:
        import django
        from django.conf import settings
        print(f"  ✅ Django {django.get_version()}")
        return True
    except Exception as e:
        print(f"  ❌ Django setup issue: {e}")
        return False

def check_database():
    """Check database connectivity"""
    print("🗄️  Checking database...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
        import django
        django.setup()
        
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            
        print("  ✅ Database connection successful")
        return True
        
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        print("     Make sure to run migrations first")
        return False

def main():
    """Main system check function"""
    print("🔍 AI Video Generation System Requirements Check")
    print("=" * 55)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages),
        ("FFmpeg", check_ffmpeg),
        ("Disk Space", check_disk_space),
        ("Django Setup", check_django_setup),
        ("Database", check_database),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        print("-" * 20)
        results[check_name] = check_func()
    
    # Summary
    print("\n" + "=" * 55)
    print("📋 SYSTEM CHECK SUMMARY")
    print("=" * 55)
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:.<30} {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Your system is ready for AI video generation.")
    elif passed >= total - 1:
        print("⚠️  Almost ready! Address the failing check above.")
    else:
        print("❌ Several issues found. Please address them before proceeding.")
    
    print("\n💡 Next steps:")
    if not results.get("Required Packages", True):
        print("1. Install missing Python packages")
    if not results.get("FFmpeg", True):
        print("2. Install FFmpeg (optional but recommended)")
    if not results.get("Database", True):
        print("3. Run database migrations")
    
    print("4. Run the setup script: python scripts/setup_video_features.py")
    
    return passed == total

if __name__ == "__main__":
    main()
