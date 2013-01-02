
## Python 2.7 Note
Because we are using unicode, if you are compiling on python 2.7, you may need to edit a tar.gz file to get this to create an egg, as below

file: /Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/tarfile.py:459
-         self.__write(self.name + NUL)
+         self.__write(self.name.encode('utf-8') + NUL)

