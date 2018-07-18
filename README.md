# Mycorrhiza
Combining phylogenetic networks and Random Forests for prediction of ancestry from multilocus genotype data.

## Running an analysis from command line (OPTION 1)

1. Install Docker

   Instructions can be found [here](https://docs.docker.com/install/).
1. (On linux, optional) [Give Docker root access](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user).

2. Get the Mycorrhiza image.
   
   ```bash
   docker pull jgeofil/mycorrhiza:latest
   ```

3. Run an analysis.
    
    Example data can be found [here](https://github.com/jgeofil/mycorrhiza/tree/master/examples/data).
    
    ```bash
    docker run -v [WORKING DIRECTORY]:/temp/ mycorrhiza crossvalidate -i /temp/[INPUT FILE] -o /temp
    ```
   
    For example, in a folder containing the input file gipsy.myc.
   
    ```bash
    docker run -v $PWD:/temp/ mycorrhiza crossvalidate -h
    docker run -v $PWD:/temp/ mycorrhiza crossvalidate -i /temp/gipsy.myc -o /temp
    ```


## Running an analysis from command line (OPTION 2)

1. Make sure you have the latest version of Python 3.x

    ```bash
    python --version
    ```

2. Install pip

   https://pip.pypa.io/en/stable/installing/

3. Install Mycorrhiza

    ```bash
    pip3 install --upgrade mycorrhiza
    ```

4. Install SplitsTree

    Installation executables for SplitsTree4 can be
    found [here](http://ab.inf.uni-tuebingen.de/data/software/splitstree4/download/welcome.html).

5. Install matplotlib

    Instructions can be found [here](https://matplotlib.org/users/installing.html).

6. Run an analysis.

   ```
   crossvalidate -h
   crossvalidate -i gipsy.myc -o out/
   ```

   It may be necessary to add to the PATH
   ```
   export PATH=$PATH:$HOME/.local/bin
   ```

## Running an analysis in a script 

### Installing Mycorrhiza with pip

1. Make sure you have the latest version of Python 3.x

    ```bash
    python --version
    ```

2. Install pip

   https://pip.pypa.io/en/stable/installing/

3. Install Mycorrhiza

    ```bash
    pip3 install --upgrade mycorrhiza
    ```

4. Install SplitsTree

    Installation executables for SplitsTree4 can be 
    found [here](http://ab.inf.uni-tuebingen.de/data/software/splitstree4/download/welcome.html).

5. Install matplotlib

    Instructions can be found [here](https://matplotlib.org/users/installing.html).

### Running an analysis in a script

1. Import the necessary modules.
    
    ```python
    from mycorrhiza.dataset import Myco
    from mycorrhiza.analysis import CrossValidate
    from mycorrhiza.plotting.plotting import mixture_plot
    ```
2. (Optional) By default Mycorrhiza will look for SplitStree in your PATH. 
I you wish to specify a different path for the SplitsTree executable you can do so in the settings module.

    ```python
    from mycorrhiza.settings import const
    const['__SPLITSTREE_PATH__'] = 'SplitsTree'
 
    ```
3. Load some data. Here data is loaded in the Mycorrhiza format from the Gipsy moth sample data file.
	Example data can be found [here](https://github.com/jgeofil/mycorrhiza/tree/master/examples/data).

    ```python
    myco = Myco(file_path='data/gipsy.myc')
    myco.load()
    ```

4. Run an analysis. Here a simple 5-fold cross-validation analysis is executed on all available loci,
without partitioning.

    ```python
    cv = CrossValidate(dataset=myco, out_path='data/')
	cv.run(n_partitions=1, n_loci=0, n_splits=5, n_estimators=60, n_cores=1)
    ```
    
5. Plot the results.

    ```python
    mixture_plot(cv)
    ```
    
## Documentation

[https://jgeofil.github.io/mycorrhiza/](https://jgeofil.github.io/mycorrhiza/)


## File formats

### Myco

Diploid genotypes occupy 2 rows (the sample identifier must be identical).

| Column(s) | Content           | Type                       |
| --------- | ----------------- | -------------------------- |
| 1         | Sample identifier | string                     |
| 2         | Population   	    | string or integer          |
| 3         | Learning flag     | {0,1}                      |
| 4 to M+3  | Loci	            | {A, T, G, C, N}            |

### STRUCTURE

Diploid genotypes occupy 2 rows (the sample identifier must be identical).

| Column(s)     | Content           | Type                       |
| ------------- | ----------------- | -------------------------- |
| 1             | Sample identifier | string                     |
| 2             | Population   	    | integer                    |
| 3             | Learning flag     | {0,1}                      |
| 4 to O+3      | Optional (Ignored)|                            |
| O+3 to M+O+3  | Loci	            | integer or -9              |

