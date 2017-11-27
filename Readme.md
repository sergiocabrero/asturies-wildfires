This repository contains code and data used in the paper:

S. Cabrero, X.G. Pañeda, D. Melendi, R. García, and T. Plagemann, "Using Firefighter Mobility Traces to Understand Ad-Hoc Networks in Wildfires," In IEEE Access, (to appear).

Feel free to use these traces or code in your own research (and please cite our paper as source!). Contact me if you have questions.

- */gps* contains GPS traces of firefighter vehicles.

- */code* contains the scripts used to analyze the data.

- */data/espanaenllamas* contains some metadata related to the wildfire. Part of this data comes from: [España en Llamas]( https://github.com/jjelosua/espanaenllamas.es-obsolete/)

- */data/simulations* contains the results of the simulations with [The ONE](https://github.com/akeranen/the-one)  

- */one* contains the mobility scenarios and the config files used to run the simulations.

To repeat the analysis in the paper, execute:

`pip install -r requirements.txt --user`

`sh 1.prepare_data.sh`

`sh 2.analyse_data.sh`

`sh 3.plot_data.sh`
