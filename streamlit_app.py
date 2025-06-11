import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io
from scipy import stats
import base64

# Page Configuration
st.set_page_config(
    page_title="SPC Diagramm Generator",
    page_icon="📊",
    layout="wide"
)

st.title("📊 SPC-Diagramm-Generator für die Produktion")
st.markdown("Statistical Process Control - Qualitätskontrolle und Prozessüberwachung")

# Sidebar Configuration
st.sidebar.header("⚙️ Konfiguration")

# Chart Type Selection
chart_type = st.sidebar.selectbox(
    "Diagrammtyp wählen:",
    ["X̄-R Karte (Mittelwert-Spannweite)", 
     "X̄-s Karte (Mittelwert-Standardabweichung)", 
     "I-MR Karte (Einzelwerte-Gleitende Spannweite)",
     "p-Karte (Anteil fehlerhaft)",
     "np-Karte (Anzahl fehlerhaft)",
     "c-Karte (Anzahl Fehler)",
     "u-Karte (Fehler pro Einheit)"]
)

# Data Input Method
data_input = st.sidebar.radio(
    "Dateneingabe:",
    ["📁 CSV-Datei hochladen", "✏️ Manuelle Eingabe", "🎲 Beispieldaten generieren"]
)

def calculate_control_limits_xbar_r(data, subgroup_size):
    """Calculate control limits for X-bar and R charts"""
    # Constants for control limits
    A2_constants = {2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483, 7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308}
    D3_constants = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0.076, 8: 0.136, 9: 0.184, 10: 0.223}
    D4_constants = {2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004, 7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777}
    
    A2 = A2_constants.get(subgroup_size, 0.577)
    D3 = D3_constants.get(subgroup_size, 0)
    D4 = D4_constants.get(subgroup_size, 2.114)
    
    # Calculate subgroup means and ranges
    subgroups = [data.iloc[i:i+subgroup_size] for i in range(0, len(data), subgroup_size) if i+subgroup_size <= len(data)]
    xbar = [group.mean() for group in subgroups]
    ranges = [group.max() - group.min() for group in subgroups]
    
    # Control limits
    xbar_mean = np.mean(xbar)
    r_mean = np.mean(ranges)
    
    ucl_xbar = xbar_mean + A2 * r_mean
    lcl_xbar = xbar_mean - A2 * r_mean
    ucl_r = D4 * r_mean
    lcl_r = D3 * r_mean
    
    return xbar, ranges, xbar_mean, r_mean, ucl_xbar, lcl_xbar, ucl_r, lcl_r

def calculate_control_limits_imr(data):
    """Calculate control limits for Individual-Moving Range charts"""
    individuals = data.values
    moving_ranges = [abs(individuals[i] - individuals[i-1]) for i in range(1, len(individuals))]
    
    mr_mean = np.mean(moving_ranges)
    x_mean = np.mean(individuals)
    
    # Constants
    d2 = 1.128  # for n=2
    D3 = 0      # for n=2
    D4 = 3.267  # for n=2
    
    ucl_x = x_mean + 2.66 * mr_mean
    lcl_x = x_mean - 2.66 * mr_mean
    ucl_mr = D4 * mr_mean
    lcl_mr = D3 * mr_mean
    
    return individuals, moving_ranges, x_mean, mr_mean, ucl_x, lcl_x, ucl_mr, lcl_mr

def calculate_control_limits_p(defects, sample_sizes):
    """Calculate control limits for p-chart"""
    p_values = [d/n for d, n in zip(defects, sample_sizes)]
    p_mean = sum(defects) / sum(sample_sizes)
    
    ucl_p = []
    lcl_p = []
    
    for n in sample_sizes:
        ucl = p_mean + 3 * np.sqrt(p_mean * (1 - p_mean) / n)
        lcl = max(0, p_mean - 3 * np.sqrt(p_mean * (1 - p_mean) / n))
        ucl_p.append(ucl)
        lcl_p.append(lcl)
    
    return p_values, p_mean, ucl_p, lcl_p

def generate_sample_data(chart_type):
    """Generate sample data for demonstration"""
    np.random.seed(42)
    n_points = 25
    
    if "X̄-R" in chart_type or "X̄-s" in chart_type:
        # Generate data for 25 subgroups of size 5
        data = []
        for i in range(n_points):
            subgroup = np.random.normal(100, 2, 5)  # Mean=100, Std=2
            data.extend(subgroup)
        return pd.DataFrame({'Messwert': data})
    
    elif "I-MR" in chart_type:
        data = np.random.normal(50, 3, n_points)
        return pd.DataFrame({'Messwert': data})
    
    elif "p-Karte" in chart_type:
        sample_sizes = np.random.randint(80, 120, n_points)
        defects = np.random.binomial(sample_sizes, 0.05)  # 5% defect rate
        return pd.DataFrame({'Stichprobengröße': sample_sizes, 'Fehlerhaft': defects})
    
    elif "np-Karte" in chart_type:
        sample_size = 100
        defects = np.random.binomial(sample_size, 0.03, n_points)
        return pd.DataFrame({'Fehlerhaft': defects})
    
    elif "c-Karte" in chart_type:
        defects = np.random.poisson(4, n_points)  # Average 4 defects per unit
        return pd.DataFrame({'Fehleranzahl': defects})
    
    elif "u-Karte" in chart_type:
        unit_sizes = np.random.uniform(0.8, 1.2, n_points)
        defects = np.random.poisson(3 * unit_sizes)
        return pd.DataFrame({'Einheitsgröße': unit_sizes, 'Fehleranzahl': defects})

# Data Input Section
if data_input == "📁 CSV-Datei hochladen":
    uploaded_file = st.file_uploader("CSV-Datei auswählen", type=['csv'])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ Datei geladen: {df.shape[0]} Zeilen, {df.shape[1]} Spalten")
        st.dataframe(df.head())
    else:
        df = None

elif data_input == "✏️ Manuelle Eingabe":
    st.subheader("Daten manuell eingeben")
    
    if "X̄-R" in chart_type or "X̄-s" in chart_type or "I-MR" in chart_type:
        manual_data = st.text_area(
            "Messwerte eingeben (ein Wert pro Zeile):",
            "100.5\n99.8\n101.2\n100.1\n99.9\n100.3\n101.0\n99.7\n100.8\n100.2"
        )
        if manual_data:
            values = [float(x.strip()) for x in manual_data.split('\n') if x.strip()]
            df = pd.DataFrame({'Messwert': values})
        else:
            df = None
    
    elif "p-Karte" in chart_type:
        col1, col2 = st.columns(2)
        with col1:
            sample_sizes = st.text_area("Stichprobengrößen:", "100\n100\n100\n100\n100")
        with col2:
            defects = st.text_area("Fehlerhaft:", "3\n5\n2\n4\n6")
        
        if sample_sizes and defects:
            sizes = [int(x.strip()) for x in sample_sizes.split('\n') if x.strip()]
            defect_counts = [int(x.strip()) for x in defects.split('\n') if x.strip()]
            df = pd.DataFrame({'Stichprobengröße': sizes, 'Fehlerhaft': defect_counts})
        else:
            df = None

else:  # Generate sample data
    df = generate_sample_data(chart_type)
    st.info("🎲 Beispieldaten wurden generiert")

# Main Analysis Section
if df is not None:
    st.subheader(f"📊 {chart_type}")
    
    # Configuration for specific chart types
    if "X̄-R" in chart_type or "X̄-s" in chart_type:
        subgroup_size = st.sidebar.slider("Stichprobengröße:", 2, 10, 5)
        
        if len(df) < subgroup_size:
            st.error(f"Nicht genügend Daten. Mindestens {subgroup_size} Werte erforderlich.")
        else:
            # Calculate control limits
            xbar, ranges, xbar_mean, r_mean, ucl_xbar, lcl_xbar, ucl_r, lcl_r = calculate_control_limits_xbar_r(df['Messwert'], subgroup_size)
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('X̄-Karte (Mittelwerte)', 'R-Karte (Spannweiten)'),
                vertical_spacing=0.1
            )
            
            # X-bar chart
            subgroup_numbers = list(range(1, len(xbar) + 1))
            
            fig.add_trace(go.Scatter(
                x=subgroup_numbers, y=xbar,
                mode='lines+markers',
                name='Mittelwerte',
                line=dict(color='blue'),
                marker=dict(size=6)
            ), row=1, col=1)
            
            # Control limits for X-bar
            fig.add_hline(y=xbar_mean, line_dash="solid", line_color="green", 
                         annotation_text=f"CL={xbar_mean:.2f}", row=1, col=1)
            fig.add_hline(y=ucl_xbar, line_dash="dash", line_color="red", 
                         annotation_text=f"UCL={ucl_xbar:.2f}", row=1, col=1)
            fig.add_hline(y=lcl_xbar, line_dash="dash", line_color="red", 
                         annotation_text=f"LCL={lcl_xbar:.2f}", row=1, col=1)
            
            # R chart
            fig.add_trace(go.Scatter(
                x=subgroup_numbers, y=ranges,
                mode='lines+markers',
                name='Spannweiten',
                line=dict(color='orange'),
                marker=dict(size=6)
            ), row=2, col=1)
            
            # Control limits for R
            fig.add_hline(y=r_mean, line_dash="solid", line_color="green", 
                         annotation_text=f"CL={r_mean:.2f}", row=2, col=1)
            fig.add_hline(y=ucl_r, line_dash="dash", line_color="red", 
                         annotation_text=f"UCL={ucl_r:.2f}", row=2, col=1)
            fig.add_hline(y=lcl_r, line_dash="dash", line_color="red", 
                         annotation_text=f"LCL={lcl_r:.2f}", row=2, col=1)
            
            fig.update_layout(height=600, showlegend=True, title_text="SPC X̄-R Regelkarte")
            fig.update_xaxes(title_text="Stichprobenummer")
            fig.update_yaxes(title_text="Mittelwert", row=1, col=1)
            fig.update_yaxes(title_text="Spannweite", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Process capability analysis
            st.subheader("📈 Prozessfähigkeitsanalyse")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Prozessmittelwert", f"{xbar_mean:.3f}")
            with col2:
                process_std = r_mean / 1.128  # d2 for subgroup size estimation
                st.metric("Prozess-Standardabweichung", f"{process_std:.3f}")
            with col3:
                st.metric("Durchschnittliche Spannweite", f"{r_mean:.3f}")
            
            # Out-of-control points analysis
            out_of_control_xbar = [i for i, x in enumerate(xbar, 1) if x > ucl_xbar or x < lcl_xbar]
            out_of_control_r = [i for i, r in enumerate(ranges, 1) if r > ucl_r or r < lcl_r]
            
            if out_of_control_xbar or out_of_control_r:
                st.warning("⚠️ Regelwidrige Punkte entdeckt!")
                if out_of_control_xbar:
                    st.write(f"X̄-Karte - Stichproben außer Kontrolle: {out_of_control_xbar}")
                if out_of_control_r:
                    st.write(f"R-Karte - Stichproben außer Kontrolle: {out_of_control_r}")
            else:
                st.success("✅ Prozess ist unter statistischer Kontrolle")

    elif "I-MR" in chart_type:
        if len(df) < 2:
            st.error("Mindestens 2 Messwerte erforderlich für I-MR Karte.")
        else:
            individuals, moving_ranges, x_mean, mr_mean, ucl_x, lcl_x, ucl_mr, lcl_mr = calculate_control_limits_imr(df['Messwert'])
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('I-Karte (Einzelwerte)', 'MR-Karte (Gleitende Spannweiten)'),
                vertical_spacing=0.1
            )
            
            # Individual values chart
            point_numbers = list(range(1, len(individuals) + 1))
            
            fig.add_trace(go.Scatter(
                x=point_numbers, y=individuals,
                mode='lines+markers',
                name='Einzelwerte',
                line=dict(color='blue'),
                marker=dict(size=6)
            ), row=1, col=1)
            
            # Control limits for individuals
            fig.add_hline(y=x_mean, line_dash="solid", line_color="green", 
                         annotation_text=f"CL={x_mean:.2f}", row=1, col=1)
            fig.add_hline(y=ucl_x, line_dash="dash", line_color="red", 
                         annotation_text=f"UCL={ucl_x:.2f}", row=1, col=1)
            fig.add_hline(y=lcl_x, line_dash="dash", line_color="red", 
                         annotation_text=f"LCL={lcl_x:.2f}", row=1, col=1)
            
            # Moving range chart
            mr_numbers = list(range(2, len(individuals) + 1))
            
            fig.add_trace(go.Scatter(
                x=mr_numbers, y=moving_ranges,
                mode='lines+markers',
                name='Gleitende Spannweiten',
                line=dict(color='orange'),
                marker=dict(size=6)
            ), row=2, col=1)
            
            # Control limits for moving ranges
            fig.add_hline(y=mr_mean, line_dash="solid", line_color="green", 
                         annotation_text=f"CL={mr_mean:.2f}", row=2, col=1)
            fig.add_hline(y=ucl_mr, line_dash="dash", line_color="red", 
                         annotation_text=f"UCL={ucl_mr:.2f}", row=2, col=1)
            fig.add_hline(y=lcl_mr, line_dash="dash", line_color="red", 
                         annotation_text=f"LCL={lcl_mr:.2f}", row=2, col=1)
            
            fig.update_layout(height=600, showlegend=True, title_text="SPC I-MR Regelkarte")
            fig.update_xaxes(title_text="Messpunkt")
            fig.update_yaxes(title_text="Einzelwert", row=1, col=1)
            fig.update_yaxes(title_text="Gleitende Spannweite", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Process analysis
            st.subheader("📈 Prozessanalyse")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Prozessmittelwert", f"{x_mean:.3f}")
            with col2:
                process_std = mr_mean / 1.128
                st.metric("Prozess-Standardabweichung", f"{process_std:.3f}")
            with col3:
                st.metric("Mittlere gleitende Spannweite", f"{mr_mean:.3f}")

    elif "p-Karte" in chart_type:
        if 'Stichprobengröße' not in df.columns or 'Fehlerhaft' not in df.columns:
            st.error("Spalten 'Stichprobengröße' und 'Fehlerhaft' erforderlich.")
        else:
            p_values, p_mean, ucl_p, lcl_p = calculate_control_limits_p(df['Fehlerhaft'], df['Stichprobengröße'])
            
            # Create p-chart
            fig = go.Figure()
            
            sample_numbers = list(range(1, len(p_values) + 1))
            
            fig.add_trace(go.Scatter(
                x=sample_numbers, y=p_values,
                mode='lines+markers',
                name='Anteil fehlerhaft',
                line=dict(color='blue'),
                marker=dict(size=8)
            ))
            
            # Control limits
            fig.add_trace(go.Scatter(
                x=sample_numbers, y=[p_mean] * len(sample_numbers),
                mode='lines',
                name=f'CL = {p_mean:.4f}',
                line=dict(color='green', dash='solid')
            ))
            
            fig.add_trace(go.Scatter(
                x=sample_numbers, y=ucl_p,
                mode='lines',
                name='UCL',
                line=dict(color='red', dash='dash')
            ))
            
            fig.add_trace(go.Scatter(
                x=sample_numbers, y=lcl_p,
                mode='lines',
                name='LCL',
                line=dict(color='red', dash='dash')
            ))
            
            fig.update_layout(
                title="SPC p-Karte (Anteil fehlerhaft)",
                xaxis_title="Stichprobenummer",
                yaxis_title="Anteil fehlerhaft",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Analysis
            st.subheader("📈 p-Karten Analyse")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Durchschnittlicher Fehleranteil", f"{p_mean:.4f}")
            with col2:
                st.metric("Durchschnittlicher Fehleranteil %", f"{p_mean*100:.2f}%")
            with col3:
                out_of_control = sum(1 for i, p in enumerate(p_values) if p > ucl_p[i] or p < lcl_p[i])
                st.metric("Punkte außer Kontrolle", out_of_control)

    # Export functionality
    st.subheader("📥 Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Diagramm als PNG herunterladen"):
            img_bytes = fig.to_image(format="png", width=1200, height=800)
            st.download_button(
                label="PNG herunterladen",
                data=img_bytes,
                file_name=f"spc_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png"
            )
    
    with col2:
        if st.button("📄 Daten als CSV herunterladen"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="CSV herunterladen",
                data=csv,
                file_name=f"spc_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

else:
    st.info("👆 Bitte laden Sie Daten hoch oder generieren Sie Beispieldaten, um zu beginnen.")

# Help Section
with st.expander("ℹ️ Hilfe und Interpretation"):
    st.markdown("""
    ## SPC-Diagramm Interpretationshilfe
    
    ### Regelkarten-Typen:
    
    **X̄-R Karte**: Für kontinuierliche Daten mit Stichproben konstanter Größe
    - Überwacht Prozessmittelwert und Variabilität
    - Stichprobengröße: 2-10 (typisch 4-5)
    
    **I-MR Karte**: Für Einzelmessungen
    - Geeignet für langsame Prozesse oder teure Tests
    - Überwacht Einzelwerte und deren Variation
    
    **p-Karte**: Für Anteil fehlerhafter Einheiten
    - Variable Stichprobengrößen möglich
    - Überwacht Qualitätsrate über Zeit
    
    ### Regelwidrige Muster:
    
    1. **Punkte außerhalb der Kontrollgrenzen**
    2. **7 aufeinanderfolgende Punkte auf einer Seite der Mittellinie**
    3. **Trends** (6+ Punkte steigend/fallend)
    4. **Zyklen** oder unnatürliche Muster
    
    ### Prozessfähigkeit:
    - **Cp**: Verhältnis von Toleranz zu Prozessstreuung
    - **Cpk**: Berücksichtigt Zentrierung des Prozesses
    - **Pp/Ppk**: Gesamtprozessfähigkeit (langfristig)
    
    ### Maßnahmen bei regelwidrigen Signalen:
    1. Sofortige Untersuchung der Ursache
    2. Korrekturmaßnahmen einleiten
    3. Prozess überwachen bis zur Stabilisierung
    4. Vorbeugende Maßnahmen implementieren
    """)

# Footer
st.markdown("---")
st.markdown("*SPC-Diagramm-Generator für Qualitätskontrolle und Prozessüberwachung*")
