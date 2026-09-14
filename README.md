# Retail Sales Performance Analysis

This project analyzes retail sales performance through a full ELT pipeline: 
	Raw sales data is loaded to AWS S3, transformed in Snowflake using Snowpark (Python), and visualized in an interactive Streamlit-in-Snowflake dashboard 
	— no external BI tools. 
	
	[-] The dashboard covers five metrics: 
		- product sales leaderboard
		- regional sales comparison
		- monthly trend analysis
		- units sold vs revenue
		- average order value 
		
	One notable finding: the North region shows a meaningfully higher AOV than East, pointing to a regional difference worth digging into further.
	
 [-] included screenshots of streamlit dashboard visual
	(as a PNG) and tagged with an underscore followed by st (_st)

 [-] sales.csv is the raw dataset included

 [-] ipynb file: snowflake/snowpark (SQL/python)
 
 [-] streamlit_app .py file: (streamlit python code for dashboard visual)