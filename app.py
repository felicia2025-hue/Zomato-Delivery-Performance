import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ========== LOAD DATA ==========
df = pd.read_csv("Zomato_Final_Dataset.csv")
df.columns = df.columns.str.strip()

if "Time_taken (min)" not in df.columns:
    st.error("Column 'Time_taken (min)' not found in the dataset!")
else:
    # ========== STREAMLIT SETUP ==========
    st.set_page_config(page_title="Zomato Dashboard", layout="wide")
    
    st.markdown("<h1 style='text-align:left; color:maroon; font-weight:bold;'>Zomato Delivery Analysis Dashboard</h1>", unsafe_allow_html=True)
    
    distance_options = ["All"] + sorted(df['DistanceCategory'].dropna().unique().tolist())
    selected_distance = st.sidebar.selectbox("Filter by Distance", options=distance_options)

    if selected_distance != "All":
        df_filtered = df[df['DistanceCategory'] == selected_distance]
    else:
        df_filtered = df.copy()

    if "multiple_deliveries" in df_filtered.columns:
        df_filtered["multiple_deliveries"] = df_filtered["multiple_deliveries"].astype(str)

    nice_labels = {
        "Road_traffic_density": "Traffic Density",
        "City": "City",
        "Festival": "Festival",
        "Weather_conditions": "Weather",
        "Vehicle_condition": "Vehicle Condition",
        "multiple_deliveries": "Workload",
        "driver_age_group": "Driver Age",
        "driver_rating_bin": "Driver Rating"
    }

    # ========== FUNCTION: BAR/COLUMN PLOT ==========
    def plot_avg_delivery(data, col, palette, ax, horizontal=False):
        display_name = nice_labels.get(col, col)
        if horizontal:
            sns.barplot(
                data=data, y=col, x="Time_taken (min)", 
                estimator="mean", palette=palette, ci=None, ax=ax
            )
            for p in ax.patches:
                value = p.get_width()
                ax.annotate(
                    f"{round(value, 1)}",
                    (p.get_x() + value/2, p.get_y() + p.get_height()/2),
                    ha='center', va='center',
                    fontsize=9, color="white", fontweight="bold"
                )
        else:
            sns.barplot(
                data=data, x=col, y="Time_taken (min)", 
                estimator="mean", palette=palette, ci=None, ax=ax
            )
            ax.tick_params(axis='x', rotation=30)
            for p in ax.patches:
                value = p.get_height()
                ax.annotate(
                    f"{round(value, 1)}",
                    (p.get_x() + p.get_width()/2, value*0.5),
                    ha='center', va='center',
                    fontsize=9, color="white", fontweight="bold"
                )
        ax.set_title(display_name, fontsize=12, color="maroon")

    # ========== TAB SETUP ==========
    tab1, tab2, tab3 = st.tabs(["External Factors", "Internal Factors", "Interactions"])
    
    red_palette = sns.color_palette(["#ff0000","#cc0000","#990000","#660000"])

# ========== TAB 1: EXTERNAL FACTORS ==========
with tab1:
    st.markdown("<h2 style='color:maroon;'>External Factors</h2>", unsafe_allow_html=True)
    external_factors = ["Road_traffic_density", "City", "Festival", "Weather_conditions"]

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    axes = axes.flatten()

    for i, col in enumerate(external_factors):
        horizontal = True if i % 2 == 1 else False
        plot_avg_delivery(df_filtered, col, red_palette, axes[i], horizontal=horizontal)

    plt.tight_layout()
    st.pyplot(fig)

    # === INSIGHT SECTION ===
    with st.expander("💡 Insights: External Factors"):
        st.markdown("""
        - **Traffic** → The **busier the traffic**, the **longer the delivery time** → congestion is a key factor in delays
        - **City** → Deliveries in **Semi-Urban areas** take the longest compared to Urban & Metropolitan → possible **infrastructure or traffic management issues**
        - **Festival** → Delivery time increases during Festivals → due to **high demand + congestion**  
        - **Weather** → Weather impact is relatively **small** compared to other factors → variations like Clear/Fog/Stormy are not significant 
        """)

# ========== TAB 2: INTERNAL FACTORS ==========
with tab2:
    st.markdown("<h2 style='color:maroon;'>Internal Factors</h2>", unsafe_allow_html=True)
    internal_factors = ["Vehicle_condition", "multiple_deliveries", "driver_age_group", "driver_rating_bin"]

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    axes = axes.flatten()

    for i, col in enumerate(internal_factors):
        horizontal = True if i % 2 == 1 else False
        plot_avg_delivery(df_filtered, col, red_palette, axes[i], horizontal=horizontal)

    plt.tight_layout()
    st.pyplot(fig)

    # === INSIGHT SECTION ===
    with st.expander("💡 Insights: Internal Factors"):
        st.markdown("""
        - **Vehicle Condition** → Poor vehicle condition slightly increases delivery time
        - **Multiple Deliveries** → Handling **>2 orders** drastically increases delivery time  
        - **Driver Age Group** → **25–34 years** fastest, while **35+** slower (likely more cautious)  
        - **Driver Rating** → High rating → deliveries are more consistent & faster  
        """)

# ========== TAB 3: INTERACTIONS ==========
with tab3:
    st.markdown("<h2 style='color:maroon;'>Interactions</h2>", unsafe_allow_html=True)

    interaction_pairs = {
        "Traffic × Weather": ("Road_traffic_density", "Weather_conditions"),
        "Vehicle Condition × Weather": ("Vehicle_condition", "Weather_conditions"),
        "Traffic × Workload": ("Road_traffic_density", "multiple_deliveries"),
        "Workload × Driver Rating": ("multiple_deliveries", "driver_rating_bin")
    }

    choice = st.radio("Select Interaction:", list(interaction_pairs.keys()))
    x_col, y_col = interaction_pairs[choice]

    pivot_table = df_filtered.groupby([x_col, y_col])["Time_taken (min)"].mean().unstack()

    fig, ax = plt.subplots(figsize=(4, 2.8))  
    sns.heatmap(
        pivot_table, annot=True, fmt=".1f", cmap="Reds", ax=ax, 
        cbar=True, annot_kws={"size":7, "color":"black"}
    )

    ax.set_xlabel(nice_labels.get(x_col, x_col), fontsize=6, color="black")  
    ax.set_ylabel(nice_labels.get(y_col, y_col), fontsize=6, color="black")
    ax.set_xticklabels(ax.get_xticklabels(), fontsize=6, rotation=45, ha="right")
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=6, rotation=0)
    ax.set_title(choice, color="maroon", fontsize=11)
    st.pyplot(fig)

    # === INSIGHT SECTION ===
    interaction_insights = {
        "Traffic × Weather": "Traffic dominates → the busier the traffic, the longer the delivery time, while weather has a smaller effect",
        "Vehicle Condition × Weather": "Poor vehicle condition combined with bad weather → increases delivery time",
        "Workload × Driver Rating": "Handling more than 3 orders drastically increases delivery time, even for highly rated drivers. Workload is the strongest factor.",
        "Traffic × Workload": "Combination of heavy traffic and multiple orders → worst-case scenario for delivery time."
    }

    with st.expander(f"💡 Insights: {choice}"):
        st.markdown(f"- {interaction_insights[choice]}")
