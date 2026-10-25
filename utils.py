import numpy as np
def filter_invalid_data(signal,min_val=-2.0,max_val=2.0):
    valid_mask=(signal>min_val)&(signal<max_val)
    cleaned_signal=signal[valid_mask]
    if len(cleaned_signal) == 0:
        return signal
    return cleaned_signal
def remove_dc_offset(signal):
    mean_dc=np.mean(signal)
    corrected_signal=signal-mean_dc
    return corrected_signal,mean_dc
def calculate_rms(signal):
    rms_value=np.sqrt(np.mean(np.square(signal)))
    return rms_value
def calculate_fft(signal,fs=10000):
    N=len(signal)
    fft_values=np.fft.fft(signal)
    fft_freq=np.fft.fftfreq(N,d=1.0/fs)
    positive_freq=fft_freq[:N//2]
    amplitude=(2.0/N)*np.abs(fft_values[:N//2])
    return positive_freq,amplitude
def classify_iso22266(omega_rms,machine_class="Class I (Precision Instruments)"):
    thresholds={"Class I (Precision Instruments)":(0.50,1.50,3.00),"Class II (Medium Machines)":(1.00,2.50,5.00),"Class III (Large Rigid Foundation)":(2.00,4.50,8.00),"Class IV (Large Flexible Foundation)":(3.00,6.00,10.00)}
    th_a,th_b,th_c=thresholds.get(machine_class,(0.50,1.50,3.00))
    if omega_rms<th_a:
        return "Zone A(Good)","#28a745","Good Condition: Newly commissioned or recently serviced machinery."
    elif omega_rms<th_b:
        return "Zone B(Satisfactory)","#17a2b8","Satisfactory condition: Acceptable for unrestricted long-term operation."
    elif omega_rms <th_c:
        return "Zone C(Unsatisfactory)","#ffc107","Unsatisfactory condition: High vibration; unsuitable for continuous long-term operation."
    else:
        return "Zone D(Unacceptable)","#dc3545","Unacceptable condition: Severe vibration; risk of immediate structural damage!" 
def apply_scale_factor(signal, scale_factor=1.0):
    return signal * scale_factor
