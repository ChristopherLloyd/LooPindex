from sage.all import *
import snappy as s



def main():
    sevens = []
    sevens.append( s.Link( [ [ 7, 14, 8, 1] , [ 13, 6, 14, 7] , [ 8, 2, 9, 1] , [ 5, 12, 6, 13] ,\
            [ 2, 10, 3, 9] , [ 11, 4, 12, 5] , [ 10, 4, 11, 3] ] ).alternating().jones_polynomial() ) #1
    sevens.append( s.Link( [[ 7, 14, 8, 1] ,[ 13, 6, 14, 7] , [ 8, 6, 9, 5] , [ 1, 12, 2, 13] ,\
          [ 9, 4, 10, 5] , [ 11, 2, 12, 3] , [ 3, 10, 4, 11] ] ).alternating().jones_polynomial() ) #2
    sevens.append( s.Link( [ [ 7, 14, 8, 1] , [ 13, 6, 14, 7] , [ 8, 2, 9, 1] , [ 5, 12, 6, 13] ,\
              [ 2, 12, 3, 11] , [ 9, 4, 10, 5] , [ 3, 10, 4, 11] ] ).alternating().jones_polynomial() ) #3
    sevens.append( s.Link( [ [ 7, 14, 8, 1] , [ 9, 6, 10, 7] , [ 13, 2, 14, 3] , [ 8, 2, 9, 1] ,\
            [ 5, 12, 6, 13] , [ 10, 4, 11, 3] , [ 11, 4, 12, 5] ] ).alternating().jones_polynomial() ) #4
    sevens.append( s.Link( [ [ 14, 7, 1, 8] , [ 8, 6, 9, 5] , [ 13, 2, 14, 3] , [ 6, 1, 7, 2] ,\
                [ 9, 13, 10, 12] , [ 4, 11, 5, 12] , [ 3, 11, 4, 10] ] ).alternating().jones_polynomial() ) #5
    sevens.append( s.Link( [ [ 14, 5, 1, 6] , [ 6, 13, 7, 14] , [ 4, 11, 5, 12] , [ 1, 11, 2, 10] , \
             [ 12, 7, 13, 8] , [ 8, 3, 9, 4] , [ 2, 9, 3, 10] ] ).alternating().jones_polynomial() ) #6
    sevens.append( s.Link( [ [ 7, 14, 8, 1] , [ 6, 11, 7, 12] , [ 13, 10, 14, 11] , [ 8, 3, 9, 4] ,\
             [ 1, 4, 2, 5] , [ 12, 5, 13, 6] , [ 2, 9, 3, 10] ] ).alternating().jones_polynomial() ) #7
    sevens.append( s.Link( [ [ 5, 14, 6, 1] , [ 4, 11, 5, 12] , [ 13, 10, 14, 11] , [ 6, 10, 7, 9] ,\
            [ 1, 9, 2, 8] , [ 12, 3, 13, 4] , [ 7, 3, 8, 2] ] ).alternating().jones_polynomial() ) #8
    sevens.append( s.Link( [ [ 5, 14, 6, 1] , [ 4, 7, 5, 8] , [ 13, 6, 14, 7] , [ 1, 10, 2, 11] ,\
            [ 8, 3, 9, 4] , [ 9, 12, 10, 13] , [ 2, 12, 3, 11] ] ).alternating().jones_polynomial() ) #9
    sevens.append( s.Link(  [ [ 5, 14, 6, 1] , [ 11, 4, 12, 5] , [ 13, 8, 14, 9] , [ 6, 2, 7, 1] ,\
            [ 3, 10, 4, 11] , [ 12, 10, 13, 9] , [ 7, 2, 8, 3] ] ).alternating().jones_polynomial() ) #10

    

    for i in range( len ( sevens ) ):
        print( i+1, sevens[i] ) 

    print()
    
    for i in range( len( sevens ) - 1 ):
        for j in range( i+1, len( sevens ) ):
            if sevens[i] == sevens[j]:
                print( i+1, "and", j+1, "have the same Jones poly" )
    
    #print( sevens )
    
    


if __name__ == "__main__":
    main()
