# 1. Initialize a counter outside the loop
if "count" not in st.session_state:
    st.session_state.count = 0

if portfolio_dict:
    while True:
        try:
            # Increment the counter each time the loop runs
            st.session_state.count += 1
            
            df, total_val = get_live_portfolio_data(portfolio_dict)
            
            with dashboard_container.container():
                # ... Metrics and Columns code remains same ...
                
                with col_left:
                    st.subheader("Asset Allocation")
                    fig = px.pie(df, values='Value', names='Ticker', hole=0.5, template="plotly_dark")
                    
                    # 2. Add the unique key here
                    st.plotly_chart(
                        fig, 
                        use_container_width=True, 
                        key=f"pie_chart_{st.session_state.count}" # <--- THIS IS THE FIX
                    )
                
                # ... Rest of your dataframe code ...

            time.sleep(refresh_rate)
