import svg2tikz
import sys
import re

# options for the command line https://xyz2tex.github.io/svg2tikz/cmdlineguide.html
# options for editing text size and style throughout file https://stackoverflow.com/questions/2237979/how-to-control-font-sizes-in-pgf-tikz-graphics-in-latex

filename = sys.argv[1]

#print( filename, type( filename ) )

f = open( filename, 'r')
toConvert = "<svg"+f.read().split( "<svg", 1)[1]

#print( toConvert)
f.close()
f = open( filename.split(".")[0]+".tex", 'w')
toWrite = svg2tikz.convert_svg(toConvert, ids=['1', '2', 'id2'], verbose=True, codeoutput="figonly", t="math")
#print( "writing", toWrite )

#bold all the text in the tikz
#splt = toWrite.split( "\\begin{tikzpicture}[",1)
#toWrite = splt[0]+"\\begin{tikzpicture}[font=\\bf,"+splt[1]

# hack it to proper math mode since the convert function isn't doing it correctly
toWrite = re.sub( "\\\\\$", "$", toWrite ) #fix escaped dollar signs
toWrite = re.sub( "\\\\\{", "{", toWrite ) #fix escaped curly brackets
toWrite = re.sub( "\\\\\}", "}", toWrite ) #fix escaped curly brackets
toWrite = re.sub( "\\\\\_", "_", toWrite ) #fix escaped underscores
toWrite = re.sub( "\\\\\^", "^", toWrite ) #fix escaped tildes
toWrite = re.sub( "\$\\\\backslash\$", "\\\\", toWrite ) #fix this annoying thing

# use the anyfontsize package to scale the font if scalefont doesn't work
# put the text on layer2 or this won't work
insert = "\\tikzstyle{every node}=[font=\\fontsize{72}{72}\\selectfont]"
splt = toWrite.split("layer2",1)
toWrite = splt[0]+"layer2\n"+insert+"\n"+splt[1]

f.write( toWrite )
f.close()