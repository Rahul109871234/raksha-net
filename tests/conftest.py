import sys 
import os 
import pathlib 
ROOT =pathlib .Path (__file__ ).parent .parent 
if str (ROOT )not in sys .path :
    sys .path .insert (0 ,str (ROOT ))