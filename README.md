# eisenmp_examples
 
Python 3.7 [Multiprocess](https://en.wikipedia.org/wiki/Multiprocessing) 
[Framework](https://en.wikipedia.org/wiki/Software_framework) for Server and Mobiles 

Examples:

* simple style prime calc to see the basic use
* simple http server on one cpu gets content via queue
* one flask orm server on each cpu - share a user db
* multiple flask orm server on each cpu, port groups - share a user db
* web download csv large list, calculate average over a column
* brute_force_attack with itertools generator and dictionary
* example with two, double fed queues
* All scenarios follow the **Template style** and have descriptions

## How to run the examples?
Clone the repo and ``run an eisenmp_exa_...``.

Brute force cracks strings of an online-game alphabet salad quest. 

    .. read wordlist .\lang_dictionaries\ger\german.dic
    .. read wordlist .\lang_dictionaries\eng\words.txt

	[BRUTE_FORCE]	cfhhilorrs

    Create processes. Default: proc/CPU core
    0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 
    
    ... proc Process-7 ... rohrschilf
    ... proc Process-14 ... rohrschilf
    ... proc Process-16 ... rohrschilf
    ... proc Process-7 ... rohrschilf
    ... proc Process-13 ... schilfrohr
    ... proc Process-13 ... schilfrohr
    ... proc Process-11 ... schilfrohr
    ... proc Process-11 ... schilfrohr

	generator empty, run time iterator 5 seconds

	exit WORKER 15
	exit WORKER 16
	exit WORKER 2
	exit WORKER 10
	exit WORKER 11
	exit WORKER 12
	exit WORKER 8
	exit WORKER 3
	exit WORKER 4
	exit WORKER 6
	exit WORKER 14
	exit WORKER 5
	exit WORKER 7
	exit WORKER 13
	exit WORKER 1
	exit WORKER 9

    --- Result for [CFHHILORRS]---
    
     rohrschilf
    
     schilfrohr

    --- END ---

	Processes are down.
    BF Time in sec: 12
    
    Process finished with exit code 0

    Inbuild example, assert a scrambled string. Use brute force or condensing.
    We use an english (.6M) plus a german (2M) wordlist and make a dictionary of it. To gain more read speed.
    (A) len(str) <=  11, combined brute force dictionary attack with a permutation generator. itertool prod. duplicates
        Permutation lists grow very fast, reaching Terabyte size.
    (B) len(str) >=  12, pre reduce a len(str) list. Kick out words which are not matching char type and count.

`eisenmp` uses Pythons permutation generator
 [itertools](https://docs.python.org/3/library/itertools.html?highlight=itertools.permutations#itertools.permutations)
for the brute force attack example.

    Another example downloads a large list and calculates average for one column.
    Python CSV extracts the column and we calculate the average with the assigned number
    of Porcesses/CPU cores. It can be more processes than CPU cores, if it makes sense.


- large lists https://www.stats.govt.nz/large-datasets/csv-files-for-download/ Crown copyright ©. 
All material Stats NZ produces is protected by Crown copyright.
Creative Commons Attribution 4.0 International licence.
- German dict https://sourceforge.net/projects/germandict/. License Public Domain
- English dict Copyright (c) J Ross Beresford 1993-1999. All Rights Reserved.
- ORM Flask-SQLAlchemy https://pypi.org/project/Flask-SQLAlchemy-Project-Template/ License MIT 44xtc44

Cheers
