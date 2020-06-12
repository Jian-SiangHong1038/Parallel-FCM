# Parallel-FCM
Fork from Contributors: Philippe Giabbanelli

# Parallel Fuzzy Cognitive Maps

Fuzzy Cognitive Mapping (FCM) represents the ‘mental model’ of individuals as a causal network equipped with an inference engine

## Download

Download from website [Parallel Fuzzy Cognitive Maps](https://osf.io/qyujt/ "Title")  

## Platform
TAMU HPRC Terra

## Version
1. Python 3.7.2
2. networkx/2.3-intel-2019a-Python-3.7.2
## Usage

```python
$ source env/bin/activate            # Activate virtual environment 
									  (Command line should show environment name on left)
```

```
$ module load Python/3.5.2-intel-2017A         # Load Python module
$ module load networkx			       # Load networkx
```

### Main is here
* `4` command line arguments:
	1. Input file with fcm configuration
	2. start point for iteration
	3. total range to be examined (an integer for which configuration of the FCM to run)
	4. output file

#### Example:
```
python greyMap.py ../caseStudy2-AllStabilizes.txt 0 1 test.txt
```

## Input File 
file at `./Experimental set-up`

**Format:** 

* Stable:
* Nodes:
* Edges:

#### Example:
```
Stable:
C1

Nodes:
C1: 0.0
C2: 0.0
C3: 0.4
C4: 0.0
C5: -0.5
C6: 0.6

Edges:
C2 C1 -0.8 -0.6
C3 C2 0.4 0.6
C3 C1 -0.5 -0.3
C4 C2 -0.5 -0.3
C5 C4 -0.3 -0.1
C5 C1 0.8 1.0
C6 C2 0.6 0.8
C6 C4 0.4 0.6
```

## Output File
file at `./Experimental set-up`

**Format:** 

* Path:
* Value of nodes:

#### Example:
```
index,C2->C1,C3->C2,C3->C1,C4->C2,C5->C4,C5->C1, ...
C1,0.9678764489729247,0.9678764489729247,0.9678764489729247,0.9678764489729247, ...
```

## Paper
[ANALYZING AND SIMPLIFYING MODEL UNCERTAINTY IN FUZZY COGNITIVE MAPS](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8247923 "Title") 

## TODO List 

- [x] `Error:` TypeError: 'NoneType' object is not subscriptable 

	File "greyMap.py", line 265, in <module>
		
		sumDict[element] = [0]*len(results[0].get()[element])
	  results[0].get() can't get any output.
	
	**SOLUTION**: There is no *reutrn output* at function *def getResults()*

- [x] TypeError: 'map' object is not subscriptable

	File "greyMap.py", line 271, in <module>
	
		print(type((result.get()[element][0])))
	
	**SOLUTION**: Because of Python 3, it's needed to add *list(map(...))*
