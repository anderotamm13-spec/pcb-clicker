# Mathtools  

---
### Usage for percent-to-coordinates/`ptc()`:  
`ptc(percent, customscreensize)`  
`percent` is a tuple of `(percentx, percenty)` showing where to place the coordinates on screen.  
`customscreensize` is an optional parameter if you need it for something else other than the game window: `(widthx, widthy)`  
`ptc()` returns a tuple for the coordinates: `(x,y)`

### Usage for percent-to-width/`ptw()`:  
`ptc(percent, width)`
`percent` is an integer to show where on width to get.
`width` is an integer showing the width of the line
`ptw()` returns an integrer

### `ptcx()` and `ptcy()`:
You pass it the percent as an integer
It returns the corresponding x/y coordinate.
Simple as that.

---

import using `from modules.mathtools import ptc, ptw`

\- wroug