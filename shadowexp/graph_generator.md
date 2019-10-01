# Generating graphs for _shadow_ library testing

Using GGen to generate sample graphs (mostly from the `dataflow-graph` option). 

## Calculating workflow costs 

* Using FLOP/s as the 'time' metric
    * System config is presented as machines that provide a given FLOP/s 
    * An application has a total amount of FLOPs required 
    * The _shadow_ library will automatically calculate this time when reading in the data files. 
    * _shadow_ also provides an option in which time is pre-calculated.
        * **Actually, lets put this into the data file**
        
        
   # What do I need?

* Generate a multiple system config files that vary the CCR
    * One Graph with comp/comm cost
    * Multiple system config files for that graph

Not sure if we need to generate CCR values on a per-system basis? 

* This could be unnecessary; we can argue CCR is simply a way of demonstrating relative data/computation rates.
 