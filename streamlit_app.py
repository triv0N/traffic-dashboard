import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
from datetime import datetime
import numpy as np

st.set_page_config(
    page_title="Traffic Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_resource
def init_connection():
    # Update this with your same connection string
    DB_URL = "postgresql://postgres:frwFu0aFGgge74QQ@db.daiunfjtxrwurgexiodd.supabase.co:5432/postgres"
    return create_engine(DB_URL)

@st.cache_data(ttl=300)
def load_data():
    engine = init_connection()
    
    query = """
    SELECT 
         title, category, content_type, url, total_traffic,
        jan_traffic, feb_traffic, mar_traffic, apr_traffic,
        may_traffic, jun_traffic, jul_traffic, aug_traffic,
        sep_traffic, oct_traffic, nov_traffic, dec_traffic
    FROM content
    ORDER BY total_traffic DESC
    """
    
    df = pd.read_sql(query, engine)
    
    monthly_cols = ['jan_traffic', 'feb_traffic', 'mar_traffic', 'apr_traffic',
                   'may_traffic', 'jun_traffic', 'jul_traffic', 'aug_traffic',
                   'sep_traffic', 'oct_traffic', 'nov_traffic', 'dec_traffic']
    
    df['avg_monthly_traffic'] = df[monthly_cols].mean(axis=1)
    df['peak_month'] = df[monthly_cols].idxmax(axis=1).str.replace('_traffic', '').str.title()
    
    return df

def main_dashboard():
    st.markdown('<h1 style="text-align: center; color: #1f77b4;">📊 Traffic Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("*Real-time content performance insights | Auto-refreshes every 5 minutes*")
    
    df = load_data()
    
    if df.empty:
        st.error("No data available.")
        return
    
    # Sidebar
    st.sidebar.header("🎛️ Dashboard Controls")
    
    if st.sidebar.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    categories = ['All'] + sorted(df['category'].unique().tolist())
    selected_category = st.sidebar.selectbox("📂 Category Filter", categories)
    
    content_types = ['All'] + sorted(df['content_type'].unique().tolist())
    selected_type = st.sidebar.selectbox("📝 Content Type", content_types)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['content_type'] == selected_type]
    
    st.sidebar.info(f"📊 Showing {len(filtered_df):,} of {len(df):,} content pieces")
    
    # Key metrics
    st.subheader("🎯 Key Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 Total Content", f"{len(filtered_df):,}")
    
    with col2:
        total_traffic = filtered_df['total_traffic'].sum()
        st.metric("📈 Total Traffic", f"{total_traffic:,.0f}")
    
    with col3:
        avg_traffic = filtered_df['total_traffic'].mean()
        st.metric("📊 Average Traffic", f"{avg_traffic:,.0f}")
    
    with col4:
        unique_categories = filtered_df['category'].nunique()
        st.metric("🎯 Categories", f"{unique_categories}")
    
    # Charts
    st.subheader("📊 Performance Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Category Performance**")
        category_stats = filtered_df.groupby('category')['total_traffic'].sum().sort_values(ascending=False).head(10)
        
        fig1 = px.bar(
            x=category_stats.values,
            y=category_stats.index,
            orientation='h',
            title='Top Categories by Total Traffic',
            color=category_stats.values,
            color_continuous_scale='Blues'
        )
        fig1.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("**📈 Traffic Distribution**")
        fig2 = px.histogram(
            filtered_df,
            x='total_traffic',
            nbins=20,
            title='Content Traffic Distribution'
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Monthly trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📅 Monthly Traffic Trends**")
        monthly_cols = ['jan_traffic', 'feb_traffic', 'mar_traffic', 'apr_traffic',
                       'may_traffic', 'jun_traffic', 'jul_traffic', 'aug_traffic',
                       'sep_traffic', 'oct_traffic', 'nov_traffic', 'dec_traffic']
        
        monthly_totals = filtered_df[monthly_cols].sum()
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        fig3 = px.line(
            x=months,
            y=monthly_totals,
            title='Monthly Traffic Trends',
            markers=True
        )
        fig3.update_traces(line_color='#1f77b4', line_width=3, marker_size=8)
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        st.markdown("**📄 Content Type Performance**")
        type_stats = filtered_df.groupby('content_type')['total_traffic'].sum().sort_values(ascending=False)
        
        fig4 = px.pie(
            values=type_stats.values,
            names=type_stats.index,
            title='Traffic Share by Content Type'
        )
        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)
    
    # Insights
    st.subheader("💡 Automated Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not filtered_df.empty:
            top_content = filtered_df.iloc[0]
            st.success(f"""
            🏆 **Top Performer**: {top_content['title'][:50]}...
            
            📊 **{top_content['total_traffic']:,.0f}** total traffic
            
            🎯 Category: **{top_content['category']}**
            """)
    
    with col2:
        best_month_idx = monthly_totals.idxmax()
        best_month = months[monthly_cols.index(best_month_idx)]
        best_traffic = monthly_totals.max()
        
        st.info(f"""
        📅 **Peak Month**: {best_month}
        
        📊 **{best_traffic:,.0f}** total traffic
        
        💡 Plan major releases for {best_month}
        """)
    
    # Top performers table
    st.subheader("🏅 Top Performing Content")
    
    top_performers = filtered_df.head(20)[
        ['title', 'category', 'content_type', 'total_traffic', 'avg_monthly_traffic']
    ].copy()
    
    top_performers['total_traffic'] = top_performers['total_traffic'].apply(lambda x: f"{x:,.0f}")
    top_performers['avg_monthly_traffic'] = top_performers['avg_monthly_traffic'].apply(lambda x: f"{x:,.0f}")
    top_performers.columns = ['Title', 'Category', 'Type', 'Total Traffic', 'Avg Monthly']
    
    st.dataframe(top_performers, use_container_width=True, hide_index=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"📊 Dashboard updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🔄 Auto-refresh: Every 5 minutes | 📈 Data points: {len(df):,}")

if __name__ == "__main__":
    main_dashboard()
