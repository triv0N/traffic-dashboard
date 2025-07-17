import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import time

def day1_rapid_setup():
    print("🚀 DAY 1: RAPID DATABASE + CSV SETUP")
    print("=" * 50)
    
    DB_URL = "postgresql://postgres:frwFu0aFGgge74QQ@db.daiunfjtxrwurgexiodd.supabase.co:5432/postgres"
    
    if "your_password" in DB_URL:
        print("❌ Please update DB_URL above with your actual Supabase connection string")
        return None
    
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return None
    
    print("\n🗄️ Step 2: Creating database tables...")
    
    create_tables_sql = """
    DROP TABLE IF EXISTS content CASCADE;
    
    CREATE TABLE content (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        category VARCHAR(100),
        content_type VARCHAR(50),
        url TEXT,
        publish_date DATE,
        total_traffic DECIMAL(15,2) DEFAULT 0,
        jan_traffic DECIMAL(12,2) DEFAULT 0,
        feb_traffic DECIMAL(12,2) DEFAULT 0,
        mar_traffic DECIMAL(12,2) DEFAULT 0,
        apr_traffic DECIMAL(12,2) DEFAULT 0,
        may_traffic DECIMAL(12,2) DEFAULT 0,
        jun_traffic DECIMAL(12,2) DEFAULT 0,
        jul_traffic DECIMAL(12,2) DEFAULT 0,
        aug_traffic DECIMAL(12,2) DEFAULT 0,
        sep_traffic DECIMAL(12,2) DEFAULT 0,
        oct_traffic DECIMAL(12,2) DEFAULT 0,
        nov_traffic DECIMAL(12,2) DEFAULT 0,
        dec_traffic DECIMAL(12,2) DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX idx_content_category ON content(category);
    CREATE INDEX idx_content_type ON content(content_type);
    CREATE INDEX idx_content_traffic ON content(total_traffic);
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(create_tables_sql))
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Table creation failed: {str(e)}")
        return None
    
    print("\n📁 Step 3: Loading and processing your CSV...")
    
    try:
        df = pd.read_csv("Traffic_Data_2024.csv")
        print(f"📊 Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        
        df = df.dropna(subset=['Title'])
        print(f"📝 After cleaning: {len(df)} valid records")
        
        monthly_cols = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        df[monthly_cols] = df[monthly_cols].fillna(0)
        df['total_traffic'] = df[monthly_cols].sum(axis=1)
        
        db_data = []
        for _, row in df.iterrows():
            record = {
                'title': str(row['Title'])[:500],
                'category': str(row['category']) if pd.notna(row['category']) else 'Uncategorized',
                'content_type': str(row['Type']) if pd.notna(row['Type']) else 'unknown',
                'url': str(row['URL']) if pd.notna(row['URL']) else '',
                'publish_date': pd.to_datetime(row['Publish date'], errors='coerce').date() if pd.notna(row['Publish date']) else None,
                'total_traffic': float(row['total_traffic']),
                'jan_traffic': float(row['January']),
                'feb_traffic': float(row['February']),
                'mar_traffic': float(row['March']),
                'apr_traffic': float(row['April']),
                'may_traffic': float(row['May']),
                'jun_traffic': float(row['June']),
                'jul_traffic': float(row['July']),
                'aug_traffic': float(row['August']),
                'sep_traffic': float(row['September']),
                'oct_traffic': float(row['October']),
                'nov_traffic': float(row['November']),
                'dec_traffic': float(row['December'])
            }
            db_data.append(record)
        
        db_df = pd.DataFrame(db_data)
        db_df.to_sql('content', engine, if_exists='replace', index=False)
        
        print(f"✅ Successfully uploaded {len(db_df)} records to database")
        
        verification_query = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT category) as unique_categories,
            SUM(total_traffic) as total_traffic,
            AVG(total_traffic) as avg_traffic
        FROM content
        """
        
        stats = pd.read_sql(verification_query, engine)
        print(f"\n📊 DATA VERIFICATION:")
        print(f"   Total records: {stats.iloc[0]['total_records']:,}")
        print(f"   Unique categories: {stats.iloc[0]['unique_categories']}")
        print(f"   Total traffic: {stats.iloc[0]['total_traffic']:,.0f}")
        print(f"   Average traffic: {stats.iloc[0]['avg_traffic']:,.0f}")
        
        return engine, db_df
        
    except FileNotFoundError:
        print("❌ Could not find 'Traffic_Data_2024.csv'")
        return None
    except Exception as e:
        print(f"❌ CSV processing failed: {str(e)}")
        return None

if __name__ == "__main__":
    print("🎯 Starting Day 1 setup...")
    result = day1_rapid_setup()
    
    if result:
        engine, data = result
        print(f"\n🏆 SUCCESS! Your database is ready with {len(data)} content pieces")
    else:
        print("❌ Setup failed - check the errors above and try again")
