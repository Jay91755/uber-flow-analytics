import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Uber", page_icon="🚗", layout="wide")

#load dataset

df = pd.read_csv("uber.csv")

#sidebar menu

with st.sidebar:
    selected = option_menu("Main Menu", ["Dataset", "Overview", "Ride Analytics", "DashBoard", "Data Assistant"],
                           icons=["table", "bar-chart", "graph-up", "cpu", "robot"],
                           menu_icon="car-front", default_index=0)

#1.dataset
if selected == "Dataset":
    st.title("Dataset Explorer")
    st.divider()

    #dataset Overview

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Row", df.shape[0])
    col2.metric("Total Column", df.shape[1])
    col3.metric("Missing Value", df.isna().sum().sum())

    st.divider()

    #col section

    st.subheader("select Columns")
    selected_cols = st.multiselect("Select Columns", df.columns, default=df.columns)
    filtered_df = df[selected_cols]

    #search dataset
    st.subheader("Search in Dataset")
    search_value = st.text_input("Search Any value")
    if search_value:
        filtered_df = filtered_df[filtered_df.astype(str).apply(
            lambda row: row.str.contains(search_value, case=False).any(), axis=1
        )]

    #col filter

    st.subheader("Column Filter")

    col1, col2 = st.columns(2)

    with col1:
        filter_col = st.selectbox("Select Column", filtered_df.columns)

    with col2:
        filter_val = st.selectbox("Select Value", filtered_df[filter_col].dropna().unique())

    if st.button("Apply Filter"):
        filtered_df = filtered_df[filtered_df[filter_col] == filter_val]
    st.divider()

    #row Display

    st.subheader("Row Display")

    row = st.slider("Number of Rows to Display", 10, len(filtered_df), 100)
    st.divider()

    #dataset Value

    st.subheader("Dataset Table")
    st.dataframe(filtered_df.head(row), use_container_width=True, hide_index=True)

    #show full dataset

    if st.checkbox("Show full dataset"):
        st.dataframe(df, use_container_width=True)
    st.divider()

    #col statistics

    st.subheader("Columns statistics")
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

    if len(numeric_cols) > 0:
        selected_cols = st.selectbox("Select Numeric Columns", numeric_cols)
        st.write(filtered_df[selected_cols].describe())
    st.divider()

    st.subheader("Download dataset")

    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Dataset", csv, "dataset.csv", "text/csv")


 #2  Overview
if selected == "Overview":
    st.title("Uber operations")
    st.divider()

    total_ride = len(df)
    completed_ride = df[df["Booking Status"] == "Completed"]
    total_revenue = completed_ride["Booking Value"].sum()
    avg_distance = completed_ride["Ride Distance"].mean()
    Success_rate = (len(completed_ride) / total_ride) * 100 if total_ride > 0 else 0
    avg_rating = completed_ride["Customer Rating"].dropna().mean()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("Gross Booking Value", f"{total_revenue:.0f}", "Target: 10000000")
    kpi2.metric("Fulfillment Rate", f"{Success_rate:.1f}%", "-2.4% From Previous Month", "red")
    kpi3.metric("Avg Trip distance", f"{avg_rating:.2f}km")
    kpi4.metric("Average Customer Rating", f"{avg_rating:.1f}⭐/5.0⭐")

    st.divider()

    #business unit performance

    st.subheader("Business unit Performance")

    bu_metrics = df.groupby("Vehicle Type").agg(
        Total_Booking=("Booking ID", "count"),
        Revenue_Generated=("Booking Value", "sum"),
        Avg_distance=("Ride Distance", "mean"),
        Avg_rating=("Customer Rating", "mean"),
    )

    bu_metrics["Revenue Share %"] = (bu_metrics["Revenue_Generated"] / total_revenue) * 100 if total_revenue > 0 else 0

    st.dataframe(
        bu_metrics.style.format({
            "Revenue_Generated": "{:.2f}",
            "Avg_distance": "{:.2f}km",
            "Avg_rating": "{:.2f}",
            "Revenue_Share %": "{:.1f}%"
        }).background_gradient(subset=["Revenue_Generated", "Total_Booking"], cmap="viridis"),
        use_container_width=True,
    )

    st.divider()

    #opration Efficiency

    col_eff, col_can = st.columns(2)

    with col_eff:
        st.subheader("Operational Efficiency")

        eff_df = df.groupby("Vehicle Type")[["Avg VTAT", "Avg CTAT"]].mean()

        st.write("Average Turnaround Time(Minutes)")
        st.dataframe(
            eff_df.style.highlight_max(axis=0, color="#800080").highlight_min(axis=0, color="#9ACD32"),
            use_container_width=True

        )

    #cancle Audit

    with col_can:
        st.subheader("Cancellation Audit")
        status_count = df["Booking Status"].value_counts().to_frame(name="Count")

        status_count["Share %"] = (status_count["Count"] / total_ride) * 100 if total_ride > 0 else 0
        st.write("Total Rides Overview")
        st.dataframe(status_count, use_container_width=True)
    st.divider()

    #financial Deep Dive

    st.subheader("Financial Operations")

    pay_col, reason_col = st.columns([4, 6])

    #payment Analysis
    with pay_col:
        st.markdown("**Payment Preference**")

        pay_summary = (completed_ride["Payment Method"].value_counts(normalize=True) * 100)
        st.dataframe(pay_summary.rename("Usage %"), use_container_width=True)

    #calcellation Reason Analysis

    with reason_col:
        st.markdown("**Primary Cancellation Triggers**")
        cust_reason = (df["Reason for cancelling by Customer"].dropna().value_counts().head(3))
        drv_reason = (df["Driver Cancellation Reason"].dropna().value_counts().head(3))

        cust_reason.index = "Customer " + cust_reason.index
        drv_reason.index = "Driver " + drv_reason.index

        reason_df = pd.concat([cust_reason, drv_reason]).to_frame()
        st.dataframe(reason_df, use_container_width=True)

    st.divider()

    #data Quality Audit

    with st.expander("Data Quality & Audit Logs"):
        audit1, audit2 = st.columns(2)
        audit1.write(f"Duplicate Records :**{df.duplicated().sum()}**")
        audit2.write(f"Missing Values:**{df["Booking Value"].isna().sum()}**")
        st.info("Missing Booking values Are expected For cancellation Or No driver Rides")
        st.success("Executive Overview Generated From Operational Dataset")

# 3. Ride Analytics
if selected == "Ride Analytics":
    st.title("Advance Ride Intelligence Dashboard")
    st.divider()

    completed = df[df["Booking Status"] == "Completed"]

    #sunbrush chart

    st.subheader("Revenue hierarchy")

    fig1 = px.sunburst(completed, path=["Vehicle Type", "Payment Method"],
                       values="Booking Value",
                       color="Booking Value",
                       color_continuous_scale="blackbody")
    fig1.update_layout(height=600)

    st.plotly_chart(fig1, use_container_width=True)
    st.divider()

    st.subheader("Revenue distribution")

    fig2 = px.treemap(completed, path=["Vehicle Type", "Payment Method"],
                      values="Booking Value",
                      color="Booking Value",
                      color_continuous_scale="brbg")
    fig2.update_layout(margin=dict(l=50, r=0, t=0, b=0), height=420)
    st.plotly_chart(fig2, use_container_width=True)
    st.divider()

    st.subheader("Customer Rating Spread")

    fig3 = px.box(completed, x="Vehicle Type", y="Payment Method", color="Vehicle Type")
    fig3.update_layout(showlegend=False, height=420)
    st.plotly_chart(fig3, use_container_width=True)
    st.divider()

    #sankey Diagram

    st.subheader("Ride Flow Analysis")
    flow = df.groupby(["Vehicle Type", "Booking Status"]).size().reset_index(name="count")
    source_label = flow["Vehicle Type"].unique().tolist()
    target_label = flow["Booking Status"].unique().tolist()

    labels = source_label + target_label

    source = flow["Vehicle Type"].apply(
        lambda x: labels.index(x)).tolist()

    target = flow["Booking Status"].apply(
        lambda x: labels.index(x)).tolist()

    value = flow["count"].tolist()

    fig4 = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="blue", width=0.5), label=labels
        ),
        link=dict(source=source, target=target, value=value)
    )])

    fig4.update_layout(height=550)
    st.plotly_chart(fig4, use_container_width=True)


#4. Dashboard
if selected == "DashBoard":

    st.title("**Visual Dashboard**")
    st.caption("This Contains Basic Visual representation Of Dataset")
    st.divider()

    f1,f2 = st.columns(2)
    completed = df[df["Booking Status"] == "Completed"]
    with f1:
        vehicle = completed["Vehicle Type"].value_counts()
        fig= px.bar(x=vehicle.index,y=vehicle.values,
                    title="Number of Rides by Vehicle Type",
                    labels={"x":"Vehicle Type","y":"Number of Rides"},
                    color = vehicle.index)

        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)


    with f2:
        revenue = completed.groupby("Vehicle Type")["Booking Value"].sum()
        fig = px.bar(x=revenue.values,y=revenue.index,orientation="h",title="Revenue By Vehicle Type",
                     labels={"x":"Revenue","y":"Vehicle Name"},
                     color = revenue.index)
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    st.divider()

    f3,f4 = st.columns(2)

    with f3:
        status = df["Booking Status"].value_counts()
        fig = px.pie(names=status.index,values=status.values,hole=0.4,
                     title="Booking Status Distribution")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    with f4:
        statu = df["Payment Method"].value_counts()
        fig= px.pie(names=statu.index,values=statu.values,title="Payment Method Distribution")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    f5,f6 = st.columns(2)

    with f5:
        fig = px.scatter(completed,x="Ride Distance",y="Booking Value",color="Vehicle Type",title="Ride Distance vs Booking Value")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    with f6:
        fig = px.histogram(completed, x="Customer Rating", nbins=35, title="Customer Rating Distribution",color="Vehicle Type")
        fig.update_traces(marker_line_width=1.5, marker_line_color="white")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    cust_reason = (df["Reason for cancelling by Customer"].dropna().value_counts())
    drv_reason = (df["Driver Cancellation Reason"].dropna().value_counts())

    cust_reason.index = "Customer " + cust_reason.index
    drv_reason.index = "Driver " + drv_reason.index

    reason_df = pd.concat([cust_reason, drv_reason])

    f7 = px.bar(x=reason_df.values,y=reason_df.index,
                     title="Cancellation Reasons Analysis",
                     color = reason_df.index,orientation="h",
                 labels={"x":"Number Of Cancellation","y":"Reasons"},)

    f7.update_layout(height=500)

    st.plotly_chart(f7, use_container_width=True)

    st.divider()

    f8,f9 = st.columns(2)
    with f8:

        avg_distance = df.groupby("Vehicle Type")["Ride Distance"].mean()

        fig = px.bar(x=avg_distance.index,y=avg_distance.values,
                     title="Average Distance by Vehicle Type",
                     labels={"x":"Vehicle Type","y":" Average Ride Distance"},
                     color = avg_distance.index)

        st.plotly_chart(fig, use_container_width=True)

    with f9:
        fig = px.histogram(completed, x="Booking Value", nbins=30, title=" Booking Value Distribution",
                            color="Vehicle Type")
        fig.update_traces(autobinx=True,marker_line_width=1.5, marker_line_color="white")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    f10 = px.scatter(completed, x="Avg CTAT", y="Avg VTAT",
                     title="Average CTAT VS Average VTAT",
                     labels={"x":"Avg CTAT","y":"Avg VTAT"},
                     color = "Vehicle Type")

    f10.update_layout(height=500)
 
    st.plotly_chart(f10, use_container_width=True)


# 5.Data Assistant

def Show_graph():
    return st.button("Show Graph")


if selected == "Data Assistant":
    st.title("Data Assistant")
    st.divider()

    st.write("Ask Questions about The dataset and Get visual analytics")
    user_question = st.text_input("Ask Your Question")

    if user_question:
        q = user_question.lower()

        completed = df[df["Booking Status"] == "Completed"]

        #Total rides

        if "total ride" in q:
            total = len(df)
            st.success(f"Total Rides in dataset: {total}")
            if Show_graph():
                status = df["Booking Status"].value_counts()

                fig = px.bar(x=status.index, y=status.values,
                             labels={"x": "Booking Status", "y": "Ride Count", },
                             title="Ride Count by Booking Status")
                st.plotly_chart(fig, use_container_width=True)

        #revenue Analysis

        elif "revenue" in q:
            revenue = completed.groupby("Vehicle Type")["Booking Value"].sum()
            st.success(f"Total Revenue: {revenue.sum():.2f}")
            if Show_graph():
                fig = px.bar(x=revenue.index, y=revenue.values,
                             title="Revenue by Vehicle Type",
                             labels={"x": "Vehicle Type", "y": "Revenue Count"})
                st.plotly_chart(fig, use_container_width=True)

        #Most used Vehicle

        elif "Vehicle" in q:
            vehicle = df["Vehicle Type"].value_counts()
            st.success(f"Total Vehicle: {vehicle.idxmax()}")

            if Show_graph():
                fig = px.pie(names=vehicle.index, values=vehicle.values,
                             title="vehicle Usage distribution")
                st.plotly_chart(fig, use_container_width=True)

        #payment analysis

        elif "payment" in q:
            payment = completed["Payment Method"].value_counts()
            if Show_graph():
                fig = px.pie(names=payment.index, values=payment.values,
                             title="Payment Methods")
                st.plotly_chart(fig, use_container_width=True)

        #Cancellation Anlysis

        elif "cancel" in q:
            cancel = df["Booking Status"].value_counts()

            if Show_graph():
                fig = px.bar(x=cancel.index, y=cancel.values,
                             title="Ride Status",
                             labels={"x": "Status", "y": "Ride Count"})
                st.plotly_chart(fig, use_container_width=True)

        #Rating analysis
        elif "rating" in q:
            st.success(f"Average Rating {completed["Customer Rating"].mean():.2f}")
            if Show_graph():
                fig = px.histogram(completed, x="Customer Rating", nbins=10, title="Customer Rating")
                st.plotly_chart(fig, use_container_width=True)

        #distance Analysis

        elif "distance" in q:
            st.success(f"Average Distance {completed["Ride Distance"].mean():.2f}")
            if Show_graph():
                fig = px.scatter(completed, x="Ride Distance", y="Booking Value", color="Vehicle Type",
                                 title="Ride Distance by Vehicle Type")
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning(
                "Please enter a valid question ..! try asking about Cancellation , revenue , vehicle type , distance, payment etc ")
            st.divider()
