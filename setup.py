#!/usr/bin/env python3
"""
Setup script for InstaForms Backend
"""
import os
import sys
import subprocess


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up InstaForms Backend...")
    
    # Check if virtual environment exists
    if not os.path.exists('venv'):
        if not run_command('python3 -m venv venv', 'Creating virtual environment'):
            sys.exit(1)
    
    # Activate virtual environment and install dependencies
    activate_cmd = 'source venv/bin/activate' if os.name != 'nt' else 'venv\\Scripts\\activate'
    
    commands = [
        (f'{activate_cmd} && pip install --upgrade pip', 'Upgrading pip'),
        (f'{activate_cmd} && pip install -r requirements.txt', 'Installing dependencies'),
        (f'{activate_cmd} && python manage.py makemigrations', 'Creating migrations'),
        (f'{activate_cmd} && python manage.py migrate', 'Running migrations'),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"\n⚠️  Setup incomplete. Please run the following manually:")
            print(f"   {activate_cmd}")
            print(f"   {command.split('&&')[-1].strip()}")
            sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Activate virtual environment:")
    print(f"      {activate_cmd}")
    print("   2. Create superuser:")
    print("      python manage.py createsuperuser")
    print("   3. Run development server:")
    print("      python manage.py runserver")
    print("\n🌐 API will be available at: http://localhost:8000/")


if __name__ == '__main__':
    main()
