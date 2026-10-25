import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import utils


# 設定網頁標題與寬版版面
st.set_page_config(page_title="FOG Vibration Diagnostic System", layout="wide")


# 主標題與副標題
st.markdown(
    "# 🔍 Fiber Optic Gyroscope (FOG) Real-Time Vibration Diagnostic System"
)
st.caption(
    "Engineering B: Real-Time Angular Vibration Diagnostics & ISO 22266"
    " Standard Evaluation"
)


# ---------------------------------------------------------
# 側邊欄：Data Import & Settings
# ---------------------------------------------------------
st.sidebar.header("⚙️ Data Import & Settings")


uploaded_file = st.sidebar.file_uploader(
    "Upload FOG Experimental Data (.xlsx / .csv)", type=["csv", "xlsx"]
)


sampling_rate = st.sidebar.number_input(
    "Sampling Rate (Hz)", value=10, step=1000
)


# Sensor Scale Factor K 設定欄位 (電壓轉角速度: deg/s per V)
scale_factor = st.sidebar.number_input(
    "Sensor Scale Factor K (deg/s per V)", value=1.00, step=0.10
)


machine_class = st.sidebar.selectbox(
    "Select ISO 22266 Machine Class",
    [
        "Class I (Precision Instruments)",
        "Class II (Medium Machines)",
        "Class III (Large Rigid Foundation)",
        "Class IV (Large Flexible Foundation)",
    ],
)


if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)


        st.sidebar.success(f"Successfully Loaded: {uploaded_file.name}")


        col_options = df.columns.tolist()
        selected_col = st.sidebar.selectbox(
            "Select Vibration Signal Column", col_options
        )


        raw_signal = (
            pd.to_numeric(df[selected_col], errors="coerce").dropna().to_numpy()
        )
        cleaned_signal = utils.filter_invalid_data(raw_signal)


        if len(cleaned_signal) == 0:
            st.error("Selected column contains no valid numerical data.")
        else:
            corrected_signal, mean_dc = utils.remove_dc_offset(cleaned_signal)


            angular_velocity_signal = utils.apply_scale_factor(
                corrected_signal, scale_factor=scale_factor
            )


            omega_rms = utils.calculate_rms(angular_velocity_signal)


            zone, color, desc = utils.classify_iso22266(
                omega_rms, machine_class=machine_class
            )


            freq, amplitude = utils.calculate_fft(
                angular_velocity_signal, fs=sampling_rate
            )


            st.markdown("---")


            # ---------------------------------------------------------
            # 區塊一：📌 Executive Summary & Health Diagnostics
            # ---------------------------------------------------------
            st.markdown("### 📌 Executive Summary & Health Diagnostics")


            col_card, col_metrics = st.columns([1.8, 1.2])


            with col_card:
                st.markdown(
                    f"""
                    <div style="background-color: {color}; padding: 32px; border-radius: 14px; color: white; min-height: 210px;">
                        <h1 style="color: white; margin: 0; font-size: 42px; font-weight: bold;">{zone}</h1>
                        <br>
                        <p style="font-size: 18px; margin: 0; line-height: 1.5; opacity: 0.95;">{desc}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


            with col_metrics:
                st.caption("RMS Angular Velocity (ISO 22266)")
                st.markdown(f"# {omega_rms:.3f} deg/s")
                st.markdown("<br>", unsafe_allow_html=True)


                d1, d2 = st.columns(2)
                with d1:
                    st.caption("DC Offset Corrected")
                    st.markdown(f"**{mean_dc:.4f} V**")
                with d2:
                    st.caption("Valid Samples Analyzed")
                    st.markdown(f"**{len(angular_velocity_signal)}**")


            st.markdown("---")


            # ---------------------------------------------------------
            # 區塊二：📌 Core Engineering Signal Analysis (連動 Time 軸更新)
            # ---------------------------------------------------------
            st.markdown("### 📌 Core Engineering Signal Analysis")


            fig_col1, fig_col2 = st.columns(2)


            with fig_col1:
                # 根據動態輸入的 sampling_rate 計算真實時間軸 (秒)
                time_axis = np.arange(len(angular_velocity_signal)) / sampling_rate


                st.markdown(
                    f"**Figure A: Time-Domain Waveform (Total"
                    f" {len(angular_velocity_signal)} points, Duration:"
                    f" {time_axis[-1]:.2f}s)**"
                )
                df_a = pd.DataFrame({
                    "Time (s)": time_axis,
                    "Amplitude (deg/s)": angular_velocity_signal,
                })
                fig_a = px.line(df_a, x="Time (s)", y="Amplitude (deg/s)")
                fig_a.update_traces(line_color="#0066cc", line_width=1.2)
                fig_a.update_layout(
                    xaxis_title=f"Time (s) - Total Duration: {time_axis[-1]:.2f} s",
                    yaxis_title="Amplitude (deg/s)",
                    height=350,
                    margin=dict(l=20, r=20, t=20, b=20),
                    plot_bgcolor="white",
                )
                st.plotly_chart(fig_a, use_container_width=True)


            with fig_col2:
                st.markdown(
                    "**Figure B: Fast Fourier Transform (FFT) Spectrum**"
                )
                df_b = pd.DataFrame(
                    {"Frequency (Hz)": freq, "Magnitude": amplitude}
                )
                fig_b = px.line(df_b, x="Frequency (Hz)", y="Magnitude")
                fig_b.update_traces(line_color="#ff0000", line_width=1.2)
                fig_b.update_layout(
                    xaxis_title="Frequency (Hz)",
                    yaxis_title="Magnitude",
                    height=350,
                    margin=dict(l=20, r=20, t=20, b=20),
                    plot_bgcolor="white",
                )
                st.plotly_chart(fig_b, use_container_width=True)


            st.markdown("---")


            # ---------------------------------------------------------
            # 區塊三：📌 Standards Reference & Raw Data
            # ---------------------------------------------------------
            st.markdown("### 📌 Standards Reference & Raw Data")


            with st.expander(
                "📖 View Complete ISO 22266 Threshold Criteria (All Machine"
                " Classes)",
                expanded=False,
            ):


                html_iso_table = """
                <table style="width: 100%; border-collapse: collapse; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; margin-top: 10px;">
                    <thead>
                        <tr style="border-bottom: 2px solid #e5e7eb; background-color: #ffffff;">
                            <th style="padding: 14px 16px; text-align: left; font-weight: 600; color: #374151; font-size: 15px; width: 28%;">Machine Class</th>
                            <th style="padding: 14px 16px; text-align: left; font-weight: 600; color: #374151; font-size: 15px; width: 18%;">Zone A (Good)</th>
                            <th style="padding: 14px 16px; text-align: left; font-weight: 600; color: #374151; font-size: 15px; width: 18%;">Zone B (Satisfactory)</th>
                            <th style="padding: 14px 16px; text-align: left; font-weight: 600; color: #374151; font-size: 15px; width: 18%;">Zone C (Unsatisfactory)</th>
                            <th style="padding: 14px 16px; text-align: left; font-weight: 600; color: #374151; font-size: 15px; width: 18%;">Zone D (Unacceptable)</th>
                        </tr>
                    </thead>
                    <tbody style="font-size: 14px; color: #111827;">
                        <tr style="border-bottom: 1px solid #f3f4f6;">
                            <td style="padding: 14px 16px; font-weight: 500;">Class I (Precision Instruments)</td>
                            <td style="padding: 14px 16px;">&le; 0.50 deg/s</td>
                            <td style="padding: 14px 16px;">&le; 1.50 deg/s</td>
                            <td style="padding: 14px 16px;">&le; 3.00 deg/s</td>
                            <td style="padding: 14px 16px;">&gt; 3.00 deg/s</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f3f4f6;">
                            <td style="padding: 14px 16px; font-weight: 500;">Class II (Medium Machines)</td>
                            <td style="padding: 14px 16px;">&le; 1.00 deg/s</td>
                            <td style="padding: 14px 16px;">&le; 2.50 deg/s</td>
                            <td style="padding: 14px 16px;">&le; 5.00 deg/s</td>
                            <td style="padding: 14px 16px;">&gt; 5.00 deg/s</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f3f4f6;">
                            <td style="padding: 14px 16px; font-weight: 500;">Class III (Large Rigid Foundation)</td>
                            <td style="padding: 14px 16px;">&le; 2.00 deg/s</td>
                            <td style="padding: 14px 16px;">&le; 4.50 deg/s</td>
                            <td style="padding: 14px 16px;">&le; 8.00 deg/s</td>
                            <td style="padding: 14px 16px;">&gt; 8.00 deg/s</td>
                        </tr>
                        <tr>
                            <td style="padding: 14px 16px; font-weight: 500;">Class IV (Large Flexible Foundation)</td>
                            <td style="padding: 14px 16px;">&le; 3.00 deg/s</td>
                            <td style="padding: 14px 16px;">&le; 6.00 deg/s</td>
                            <td style="padding: 14px 16px;">&le; 10.00 deg/s</td>
                            <td style="padding: 14px 16px;">&gt; 10.00 deg/s</td>
                        </tr>
                    </tbody>
                </table>
                """
                st.markdown(html_iso_table, unsafe_allow_html=True)


            with st.expander("📊 View Uploaded Raw Dataset"):
                st.dataframe(df)


    except Exception as e:
        st.error(f"An error occurred during analysis: {e}")
else:
    st.info("👈 Please upload a data file from the sidebar to begin analysis.")
