## Inkscape Extension: Bingo Card Creator

Adds "Bingo Card Creator" to the Inkscape Extensions list.

### How To Install

Copy the bingo folder from this repository into the Inkscape extensions folder.

Works with Inkscape 1.2

### How To Use

* Open Extensions > Render > Bingo Card Creator
* Set parameters as necessary and apply

![Bingo params preview](resources/preview.jpg)

## Bingo Templates

When a template has been opened in Inkscape before this extension is run, it will insert the bingo numbers into the predefined area(s).

### How To Build A Template For The Bingo Card Creator

Templates can predefine a single or multiple areas were the bingo numbers should be placed in.

Create a rectangle and set the id-attribute to `bingo-area`. For multiple areas append numbers to the id such as `bingo-area_1`. Clones of rectangles or clones of groups with bingo-area rectangles can also be used as bingo-areas.

Use Inkscapes XML-Editor to add following attributes to the bingo-area-rectangle (optional):

|Attribute           |Type   |Description
|--------------------|-------|-----------|
|bingo-font-size     |float  |Font Size
|bingo-columns       |int    |Number of columns
|bingo-rows          |int    |Number of rows
|bingo-column-range  |int    |Number range for each column
|bingo-free-rows     |int    |Count of random free spaces in each row (british bingo)
|bingo-free          |x.y;x.y|Semicolon (;) separated positions for free spaces. X and Y coordinates will be separated by a dot (.)
|bingo-star          |boolean|If set to true, the number in the center will be replaced by a star
|bingo-render-grid   |boolean|If set to true a grid will be rendered
|bingo-headline      |string |The headline text
|bingo-headline-color|color  |Headline color
|bingo-color         |color  |The color for the numbers

If an attribute remains undefined, settings from user input will apply. Attributes of previous bingo-areas in the document will be applied to next areas (if not redefined).

For a better understanding have a look at the [template example file](resources/template_example.svg) in this repository.