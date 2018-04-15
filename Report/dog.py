def careForDog(dog,isHungry,isHome):
    if isHungry == True:
        if isHome == True:
            dog.Feed()
        else:
            dog.Locate()
            dog.Feed()
    else:
        if isHome == False:
            dog.Locate()
        else:
            # Do nothing
