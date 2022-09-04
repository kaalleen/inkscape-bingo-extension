## Inkscape Extension: Bingo Card Creator

Adds "Bingo Card Creator" to the Inkscape Extensions list.

### How to install

Copy the bingo folder from this repository into the Inkscape extensions folder.

Works with Inkscape 1.2

### How to use

* Open Extensions > Render > Bingo Card Creator
* Set parameters as necessary and apply

![Bingo params preview](preview.jpg)

## Bingo Templates

When a template has been opened in Inkscape before this extension is run, it will insert the bingo numbers into the predefined area(s).

### How to Build Template for the Bingo Card Creator

Templates can predefine areas were the bingo numbers should be placed in. The area is created through a rectangle with an id-attribute starting with `bingo-area`. Multiple areas are possible - in this case use `bingo-area_1` etc. as ids for the rectangles.

All available parameters can be forced through the template author. Set the following attributes to the bingo-area-rectangle:

|Attribute|Values|Default|Description|
|---|---|---|---|
|bingo-font-size|float|10|Font Size|
|bingo-columns|int|5|Number of columns|
|bingo-rows|int|5|Number of rows|
|bingo-column-range|int|15|Number range for each column|
|bingo-free|x.y;x.y|none|Semicolon (;) separated positions for free spaces. X and Y coordinates will be separated by a dot (.)|
|bingo-star|boolean|false|If set to true, the number in the center will be replaced by a star|
|bingo-render-grid|boolean|true|If set to true a grid will be rendered|
|bingo-headline|string|BINGO|The headline text|
|bingo-headline-color|color|'#e01b24'|Headline color|
|bingo-color|color|black|The color for the numbers|

Use Inkscapes XML-Editor to add the attributes. Attributes of the first bingo-area in the document will be applied to all following areas (if not redefined).

For a better understanding have a look at the [template example file](template_example.svg) in this repository.