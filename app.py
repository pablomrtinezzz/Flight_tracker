import streamlit as st
import pandas as pd
from src.database import get_all_stats, get_current_top_flights, get_historical_average

# Configure Dashboard UI
st.set_page_config(page_title="Radar de Vuelos MAD ⇄ LPA", layout="wide", initial_sidebar_state="collapsed")

st.title("✈️ Radar de Vuelos Inteligente: MAD ⇄ LPA")
st.markdown("Algoritmo de seguimiento en tiempo real basado en el análisis de los **4 mejores vuelos disponibles**.")

stats_data = get_all_stats()

if not stats_data:
    st.info("Esperando a que el rastreador recolecte los primeros datos...")
else:
    # Prepare historical dataframe
    df_stats = pd.DataFrame(stats_data, columns=["Fecha", "Mes", "Media (Top 4)", "Mínimo Absoluto"])
    df_stats['Fecha'] = pd.to_datetime(df_stats['Fecha']).dt.strftime('%d-%b %H:%M')

    # Create Tabs for cleaner UI
    tab_jul, tab_ago = st.tabs(["🌞 Julio 2026", "🏖️ Agosto 2026"])

    for tab, month_name in zip([tab_jul, tab_ago], ["Julio 2026", "Agosto 2026"]):
        with tab:
            df_month = df_stats[df_stats["Mes"] == month_name].copy()

            if not df_month.empty:
                # Key Performance Indicators (KPIs)
                latest_min = df_month.iloc[0]["Mínimo Absoluto"]
                global_avg = get_historical_average(month_name)
                variance = latest_min - global_avg if global_avg else 0

                col1, col2, col3 = st.columns(3)
                col1.metric(label="Precio Mínimo Actual", value=f"{latest_min:.2f} €",
                            delta=f"{variance:.2f} € vs Media", delta_color="inverse")
                col2.metric(label="Media Histórica", value=f"{global_avg:.2f} €" if global_avg else "Calculando...")
                col3.info("🎯 **Estrategia:** La alerta suena si el mínimo cae 20€ por debajo de la media histórica.")

                st.write("---")

                # Layout for Charts and Top Flights
                col_chart, col_table = st.columns([3, 2])

                with col_chart:
                    st.subheader("📈 Tendencia de Precios")
                    if len(df_month) > 1:
                        # Multi-line chart showing both Average and Min Price
                        chart_data = df_month.set_index("Fecha")[["Media (Top 4)", "Mínimo Absoluto"]]
                        st.line_chart(chart_data, color=["#FF4B4B", "#00FF00"])
                    else:
                        st.warning("Recopilando datos para generar la gráfica (se necesitan al menos 2 ejecuciones).")

                with col_table:
                    st.subheader("🏆 Top 4 Vuelos Actuales")
                    top_flights = get_current_top_flights(month_name)

                    if top_flights:
                        df_top = pd.DataFrame(top_flights, columns=["Ranking", "Precio", "Ida", "Vuelta", "Comprar"])

                        st.dataframe(
                            df_top,
                            column_config={
                                "Ranking": st.column_config.NumberColumn(format="🏆 %d"),
                                "Precio": st.column_config.NumberColumn(format="%.2f €"),
                                "Comprar": st.column_config.LinkColumn("🔗 Link Skyscanner")                            },
                            hide_index=True,
                            use_container_width=True
                        )
                    else:
                        st.error("No hay vuelos activos en este momento.")