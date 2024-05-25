from subprocess import call #used for running external scripts
#import shutil
filename = "tex/spheriloops"
call(['pdflatex', '--shell-escape', '-halt-on-error', '-output-directory', filename.split("/")[0], filename+".tex"])
#call twice to fix references
call(['bibtex',filename])
call(['pdflatex', '--shell-escape', '-halt-on-error', '-output-directory', filename.split("/")[0], filename+".tex"])
call(['pdflatex', '--shell-escape', '-halt-on-error', '-output-directory', filename.split("/")[0], filename+".tex"]) 
#try:
    #os.remove(filename+".aux")
    #os.remove(filename+".log")
    #os.remove(filename+".toc")
#    shutil.rmtree( "svg-inkscape/" )
#except FileNotFoundError:
#    pass
