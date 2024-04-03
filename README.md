This project is a solution for impedance tube measurements and the following analysis of the experimental data. It is written for a standing wave method (ISO-10534-1).

Ascending_Frequency_2.0.2 does 3 things in parallel:

    plays single sine frequencies
    records a microphone
    controls a stepper motor using an arduino

Please use a computer with at least 3 cores to avoid issues of synchronicity. The script saves the measurement data inside a csv file.

MK4_Auswertung uses the csv data for further analysis. It calculates the reflection coefficient and saves it into numpy arrays.
