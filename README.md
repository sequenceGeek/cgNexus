
#cgNexus

Nexus is flat file loader (think tab spaced files) that:
	* Easily loads and saves defined file formats
	* Automatically casts values (from flat file) to python types when loaded inside scripts  
	* Automatically assigns attribute names to file columns for speedier development time (think 'geneName' instead of column[5])
	* Eases line independent parallel processes (split file --> compute --> stitch file back together)
	* Does other stuff (e.g., eases the creation of mappings based on file columns)

Advantages:
	* Much faster development time!

Disadvantages (no free lunch :( ):
	* slower running time
	* often greater memory usage
		

TODO:
  X 1) make attributes properties for non-[id] access
        a) this means make internal id tracker
    2) load everything on init (call it hints)
		a) This will be optional with (4) implemented
			i) if used it will boost speed
		b) Hints will be a single string
			i) e.g., 'geneName,geneLength'
  X 3) make format files just a txt file 
        a) need good way to access them...
    4) load items as they are needed
        b) this is complicated cuz going through file every time
        you need to load something is SLOOOOW? or is it?
    5) fix the copy issue, should be able to return default w/o copy
    6) create add/delete row from Nexus
		a) if an id is added mid loop, will that change generator for while loop?
    7) Nexus Generator (do not load data into memory, but still cast)
		a) read only?
		b) its possible to use the generator to save to ANOTHER FILE while running...
	8) load without format
		a) quickFormat('0 geneName string .', '3 partnerIDs intList 1,2,3')
	9) Simplify Parallel Processing with helper scripts
		a) using SGE (Sun Grid Engine)
		b) without SGE
		c) split/ compute/ stitch using exitSignals(not OS specific)
	10) check if runs on Windows
	11) add running from command line script...
	12) add Errors for common mishaps...

SPEED
	-replace split with [:-1]
	-use str.split as splitIt (no dot)
    -[possibly switch to regex (NO...much slower...)]
	-try to get rid of for loops (use comprehension/map)
	-optimize casting fxns

Documentation
	1) Show usages for:
		a) loading/saving a tab file 
			i) make format file
			ii) load file/ update item / save file
		b) using a quick table to load
		c) add row/delete row
		d) run simple job in parallel 
			i) explain that job has to be row-independent

Development:
	1) Use Trello?
