# Mycorrhiza
Combining phylogenetic networks and Random Forests for prediction of ancestry from multilocus genotype data.

## Installing Mycorrhiza with pip

1. Make sure you have the latest version of Python 3.x

    ```bash
    python --version
    ```

2. Install pip

    ```bash
    python -m pip install --upgrade pip setuptools wheel
    ```

3. Install Mycorrhiza

    ```bash
    pip install --upgrade mycorrhiza
    ```

4. Install SplitsTree

    Installation executables for SplitsTree4 can be 
    found [here](http://ab.inf.uni-tuebingen.de/data/software/splitstree4/download/welcome.html).
    
## Running an analysis

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

