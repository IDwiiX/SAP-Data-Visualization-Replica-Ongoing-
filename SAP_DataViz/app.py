import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import io
import base64
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load the dataset
data = pd.read_csv("data/sales_data.csv")
data["Date"] = pd.to_datetime(data["Date"])

# Define the app layout
app.layout = html.Div([
    
    dbc.Container([
        html.H1("SAP Data Visualization Replica", style={"text-align": "center", "padding": "20px"}),
        html.H2("Developed by The MAK Project", style={"text-align": "center", "margin-bottom": "30px"}),
        
        # Sales summary panel with padding
        html.Div([
            html.H4("Sales Summary", style={"text-align": "center", "margin-top": "20px"}),
            html.Div(id="sales-summary", style={"text-align": "center", "padding": "10px"})
        ], style={"border": "1px solid #ddd", "border-radius": "5px", "background-color": "#f9f9f9", "margin-bottom": "30px"}),
        
        # Region filter
        html.P("Select regions to compare sales data:", style={"margin-bottom": "10px"}),
        dcc.Checklist(
            id="region-checkboxes",
            options=[{"label": region, "value": region} for region in data["Region"].unique()],
            value=["North"],  # Default selection
            inline=False,  # Display checkboxes horizontally
            style={"margin-bottom": "20px"}
        ),
        
        # Date Range Picker
        dcc.DatePickerRange(
            id="date-picker-range",
            start_date=data["Date"].min().date(),  # Start date
            end_date=data["Date"].max().date(),  # End date
            display_format="YYYY-MM-DD",  # Date format
            style={"margin-top": "20px", "margin-bottom": "30px"}
        ),
        
        # Bar chart for sales by region
        dcc.Loading(
            id="loading",
            children=[dcc.Graph(id="bar-chart", style={"height": "400px"}), 
                      dcc.Graph(id="line-chart", style={"height": "400px"})],
            type="circle"
        ),
        
        # Pie chart for sales distribution
        html.Div([
            dcc.Graph(id="pie-chart", style={"height": "400px"})
        ], style={"margin-top": "30px"}),
        
        # Export button
        html.Button(
            id="export-button",
            children="Export Data",
            style={"margin-top": "20px", "width": "200px"}
        ),
    ])
])

# Callback to update the bar chart, line chart, pie chart, and sales summary
@app.callback(
    [Output("bar-chart", "figure"),
     Output("line-chart", "figure"),
     Output("pie-chart", "figure"),
     Output("sales-summary", "children"),
     Output("export-button", "href")],
    [Input("region-checkboxes", "value"),
     Input("date-picker-range", "start_date"),
     Input("date-picker-range", "end_date")]
)
def update_charts_and_summary(selected_regions, start_date, end_date):
    # Filter data based on the selected regions and date range (no category filter)
    filtered_data = data[
        (data["Region"].isin(selected_regions)) &
        (data["Date"] >= pd.to_datetime(start_date)) &
        (data["Date"] <= pd.to_datetime(end_date))
    ]
    
    # Create a bar chart with custom colors
    bar_fig = px.bar(filtered_data, x="Region", y="Sales", title="Sales by Region", hover_data=["Region", "Sales"])
    bar_fig.update_traces(marker_color='rgba(255, 99, 132, 0.6)')  # Set color for bars
    bar_fig.update_layout(title=f"Sales by Region from {start_date} to {end_date}")

    # Create a line chart with custom colors
    line_fig = px.line(filtered_data, x="Date", y="Sales", color="Region", title="Sales Trends Over Time")
    line_fig.update_traces(line=dict(color='rgba(54, 162, 235, 0.6)', width=4))  # Set line color

    # Create a pie chart for sales distribution by region
    pie_fig = px.pie(filtered_data, names="Region", values="Sales", title="Sales Distribution by Region")
    
    # Calculate sales summary
    total_sales = filtered_data["Sales"].sum()
    average_sales = filtered_data["Sales"].mean()
    highest_sales = filtered_data["Sales"].max()
    
    # Create the sales summary display
    summary_text = f"""
    Total Sales: ${total_sales:,.2f}
    Average Sales: ${average_sales:,.2f}
    Highest Sales: ${highest_sales:,.2f}
    """
    
    # Prepare the export link for CSV
    csv_string = filtered_data.to_csv(index=False)
    csv_bytes = io.BytesIO(csv_string.encode())
    b64_csv = base64.b64encode(csv_bytes.getvalue()).decode()
    export_link = f"data:text/csv;base64,{b64_csv}"

    return bar_fig, line_fig, pie_fig, summary_text, export_link

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
