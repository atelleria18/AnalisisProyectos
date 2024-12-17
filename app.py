import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Analisis de Proyectos",
    layout="wide",  # This makeas the main content wider
    page_icon="B.jpg"  # Optional: Add an emoji as your app icon
)
st.sidebar.image("logo.png", width=200) 

# Title and File Loading
st.title("Analisis de Proyectos")

# File Upload
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])


if uploaded_file:
    # Load Data
    @st.cache_data
    def load_data(file):
        df = pd.read_excel(file)
        for col in df.columns:
            if df[col].dtype == 'object' or df[col].dtype == 'mixed':
                df[col] = df[col].astype(str)
        df['globalProject'] = df['globalProject'].str.upper()
        df['projectName'] = df['projectName'].str.upper()
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['time (hours)'] = df['time (minutes)'] / 60
        return df

    df = load_data(uploaded_file)

    # Sidebar Filters
    st.sidebar.header("Filters")
    start_date = st.sidebar.date_input("Start Date", df['Date'].min())
    end_date = st.sidebar.date_input("End Date", df['Date'].max())
    filtered_data = df[(df['Date'] >= pd.Timestamp(start_date)) & (df['Date'] <= pd.Timestamp(end_date))]

    for col in ['department', 'globalProject', 'user']:
        unique_vals = filtered_data[col].dropna().unique()
        selected_vals = st.sidebar.multiselect(f"Filter {col}", unique_vals, default=unique_vals)
        filtered_data = filtered_data[filtered_data[col].isin(selected_vals)]

    # Display Filtered Data
    st.subheader("Filtered Data")
    st.dataframe(filtered_data)

    # Total Hours
    total_hours = filtered_data['time (hours)'].sum()
    st.subheader(f"Total Hours: {total_hours:.2f} hours")

    # Visualization Options
    st.subheader("Visualization Options")
    chart_type = st.selectbox("Choose a chart type", ["Pie Chart", "Bar Plot", "Grouped Bar Plot"])

    # PIE CHART
    if chart_type == "Pie Chart":
        pie_col = st.selectbox("Select column for Pie Chart", options=filtered_data.columns)
        pie_data = filtered_data.groupby(pie_col)['time (hours)'].sum().reset_index()

        # Plotly Styled Pie Chart
        fig = px.pie(
            pie_data,
            names=pie_col,
            values='time (hours)',
            title=f"Total Hours by {pie_col} (Total: {total_hours:.2f} hours)",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Aggrnyl  # Use a clean color palette
        )
        fig.update_traces(
            textinfo='none',  # Suppress default text
            hovertemplate="<b>%{label}</b><br>Hours: %{value:.2f}<br>Percentage: %{percent}",
            texttemplate="<b>%{percent}</b><br>%{value:.2f} hrs",  # Two-line label
            textposition='inside'
        )
        fig.update_layout(
            font=dict(size=14, family="Arial", color="black"),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig)

    # BAR PLOT
    elif chart_type == "Bar Plot":
        x_col = st.selectbox("Select X-axis column", options=filtered_data.columns)
        y_col = 'time (hours)'

        if x_col == 'Date':
            filtered_data['Month'] = filtered_data['Date'].dt.to_period('M').astype(str)
            bar_data = filtered_data.groupby('Month')[y_col].sum().reset_index()
            x_col = 'Month'
        else:
            bar_data = filtered_data.groupby(x_col)[y_col].sum().reset_index()

        # Plotly Styled Bar Chart
        fig = px.bar(
            bar_data,
            x=x_col,
            y=y_col,
            text=y_col,
            title=f"Total Hours by {x_col} (Total: {total_hours:.2f} hours)",
            color=x_col,
            color_discrete_sequence=px.colors.sequential.Aggrnyl
        )
        fig.update_traces(
            texttemplate='%{text:.2f}', textposition='outside'
        )
        fig.update_layout(
            font=dict(size=14, family="Arial"),
            xaxis_title=x_col,
            yaxis_title="Hours",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig)

    # GROUPED BAR PLOT
    elif chart_type == "Grouped Bar Plot":
        x_col = st.selectbox("Select X-axis column", options=filtered_data.columns)
        group_col = st.selectbox("Select Grouping column", options=filtered_data.columns)
        y_col = 'time (hours)'

        if x_col == 'Date':
            filtered_data['Month'] = filtered_data['Date'].dt.to_period('M').astype(str)
            grouped_data = filtered_data.groupby(['Month', group_col])[y_col].sum().reset_index()
            x_col = 'Month'
        else:
            grouped_data = filtered_data.groupby([x_col, group_col])[y_col].sum().reset_index()

        # Plotly Styled Grouped Bar Chart
        fig = px.bar(
            grouped_data,
            x=x_col,
            y=y_col,
            color=group_col,
            barmode='group',
            text_auto='.2f',
            title=f"Total Hours by {x_col} and {group_col} (Total: {total_hours:.2f} hours)",
            color_discrete_sequence=px.colors.sequential.Aggrnyl
        )
        fig.update_layout(
            font=dict(size=14, family="Arial"),
            xaxis_title=x_col,
            yaxis_title="Hours",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig)

    st.sidebar.text("BIOLAN - Styled Visualization")
