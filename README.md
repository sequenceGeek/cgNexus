#cgNexus

**Nexus is flat file (text file) loader that:**
	
 * Easily loads and saves pre-defined tab spaced column files
 * Automatically casts values (from flat file) to python types on load  
 * Automatically assigns attribute names to file columns for use in script (think 'geneName' instead of column[5])
 * Eases execution of line-independent parallel processes (split file --> compute --> stitch file back together)
 * Does more (e.g., eases the creation of attribute mappings based on file columns)

**Advantages**
 
 * Much faster development time!

**Disadvantages**
 
 * slower running time
		

##TODO
 
 * Make attributes properties for non-[id] access (X)
   * this means make internal id tracker
 * Load everything on init (call it hints) (X)
   * This will be optional with (4) implemented
     *If used it will boost speed.
   * Hints will be a single string
     * e.g., 'geneName,geneLength'
 * Make format files just a txt file (X) 
   * need good way to access them...
 * Load items as they are needed (X)
   *this is complicated cuz going through file every time you need to load something is SLOOOOW? or is it?
 * Fix the copy issue, should be able to return default w/o copy (X)
    * use list[:] instead of copy...much faster (also faster than list(list)) 
 * Create add/delete row from NX.
   * if an id is added mid loop, will that change generator for while loop?
 * Nexus Generator (do not load data into memory, but still cast it)
   * read only?
   * its possible to use the generator to save to ANOTHER FILE while running...
 * Load without format
   * quickFormat('0 geneName string .', '3 partnerIDs intList 1,2,3')
 * Simplify Parallel Processing with helper scripts
   * using SGE (Sun Grid Engine)
   * without SGE
   * split/ compute/ stitch using exitSignals(not OS specific)
 * Check if runs on Windows
 * Add running from command line script...
 * Add Errors for common mishaps...

##Speed

 * replace split with [:-1]
 * use str.split as splitIt (no dot)
 * [possibly switch to regex (NO...much slower...)]
 * try to get rid of for loops (use comprehension/map)
 * optimize casting fxns

##Documentation

 * Show usages for:
   * Loading/saving a tab file 
     * Make format file
     * Load file/ update item / save file
    * Using a quick table to load
    * Add row/delete row
    * Run simple job in parallel 
      * Explain that job has to be row-independent


