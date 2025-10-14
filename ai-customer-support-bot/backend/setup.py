#!/usr/bin/env python3
"""
Setup script to initialize the AI Customer Support Bot
This script will:
1. Create database tables
2. Load sample FAQ data
3. Verify the setup
"""

import json
import os
import sys
from pathlib import Path

# Add the backend directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db, get_db
from models import FAQ
from dotenv import load_dotenv

def load_sample_faqs():
    """Load sample FAQ data from JSON file"""
    
    # Path to sample FAQs
    faq_file = Path(__file__).parent.parent / "data" / "sample_faqs.json"
    
    if not faq_file.exists():
        print(f"❌ Sample FAQ file not found: {faq_file}")
        return False
    
    try:
        with open(faq_file, 'r', encoding='utf-8') as f:
            faqs_data = json.load(f)
        
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Check if FAQs already exist
            existing_count = db.query(FAQ).count()
            if existing_count > 0:
                print(f"📝 Database already contains {existing_count} FAQs")
                response = input("Do you want to clear existing FAQs and reload? (y/N): ").strip().lower()
                if response == 'y':
                    db.query(FAQ).delete()
                    db.commit()
                    print("🗑️ Cleared existing FAQs")
                else:
                    print("✅ Keeping existing FAQs")
                    return True
            
            # Load FAQs
            loaded_count = 0
            for faq_data in faqs_data:
                faq = FAQ(
                    question=faq_data['question'],
                    answer=faq_data['answer'],
                    category=faq_data['category'],
                    keywords=faq_data.get('keywords'),
                    priority=faq_data.get('priority', 1)
                )
                db.add(faq)
                loaded_count += 1
            
            db.commit()
            print(f"✅ Successfully loaded {loaded_count} FAQs into the database")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error loading FAQs: {e}")
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error reading FAQ file: {e}")
        return False

def verify_setup():
    """Verify that the setup was successful"""
    
    try:
        # Test database connection
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Check FAQ count
            faq_count = db.query(FAQ).count()
            
            # Check FAQ categories
            categories = db.query(FAQ.category).distinct().all()
            category_list = [cat[0] for cat in categories]
            
            print("\\n🔍 Setup Verification:")
            print(f"   📊 Total FAQs: {faq_count}")
            print(f"   📂 Categories: {', '.join(category_list)}")
            
            if faq_count > 0:
                print("✅ Database setup verified successfully!")
                return True
            else:
                print("⚠️ No FAQs found in database")
                return False
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Setup verification failed: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    
    env_file = Path(__file__).parent.parent / ".env"
    env_example = Path(__file__).parent.parent / ".env.example"
    
    if env_file.exists():
        print("📝 .env file already exists")
        return True
    
    if env_example.exists():
        try:
            # Copy .env.example to .env
            with open(env_example, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ Created .env file from .env.example")
            print("⚠️ Please update the Gemini API key in .env file before running the bot")
            return True
            
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("❌ .env.example file not found")
        return False

def main():
    """Main setup function"""
    
    print("🤖 AI Customer Support Bot Setup")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Create .env file if needed
    print("\\n1. Checking environment configuration...")
    create_env_file()
    
    # Initialize database
    print("\\n2. Initializing database...")
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    # Load sample FAQs
    print("\\n3. Loading sample FAQ data...")
    if not load_sample_faqs():
        print("⚠️ FAQ loading failed, but you can add FAQs later via the API")
    
    # Verify setup
    print("\\n4. Verifying setup...")
    success = verify_setup()
    
    print("\\n" + "=" * 40)
    
    if success:
        print("🎉 Setup completed successfully!")
        print("\\nNext steps:")
        print("1. Update your Gemini API key in the .env file")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run the server: python backend/main.py")
        print("4. Open http://localhost:8000 in your browser")
    else:
        print("❌ Setup completed with errors")
        print("Please check the error messages above and try again")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)